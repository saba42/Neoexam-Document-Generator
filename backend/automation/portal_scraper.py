import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def scrape_parameters(portal_url: str, email: str, password: str, course_name: str, module_name: str, test_name: str) -> list[dict]:
    """
    Automates the portal login, course navigation, and parameter extraction
    using exact CSS selectors provided by the user.
    """
    # 0. Sanitize URL
    portal_url = portal_url.strip()
    if not portal_url.startswith("http://") and not portal_url.startswith("https://"):
        portal_url = "https://" + portal_url
        
    checked_parameters = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        
        try:
            # ======================
            # 1. LOGIN FLOW
            # ======================
            try:
                await page.goto(portal_url, wait_until="networkidle", timeout=120000)
            except Exception as e:
                raise Exception(f"Failed to navigate to {portal_url}: {str(e)}")

            try:
                # Fill email
                await page.wait_for_selector("#emailAddress", state="visible", timeout=20000)
                # Instead of standard 'fill', we use fill + dispatch_event to ensure Angular picks it up
                await page.locator("#emailAddress").fill(email)
                await page.locator("#emailAddress").dispatch_event("input")
                await page.locator("#emailAddress").dispatch_event("change")
                
                # Fill password
                await page.wait_for_selector("#password", state="visible")
                await page.locator("#password").fill(password)
                await page.locator("#password").dispatch_event("input")
                await page.locator("#password").dispatch_event("change")
                
                # Small wait between events
                await asyncio.sleep(1)
                
                # Try clicking the login button directly using Playwright locator
                login_btn = page.locator('button.form__button[label="Login"]')
                if await login_btn.count() > 0:
                    await login_btn.click(force=True, no_wait_after=True)
                else:
                    # Fallback to Enter key
                    await page.press("#password", "Enter")
                
                # Wait for the URL to change away from login
                try:
                    await page.wait_for_url(lambda url: "login" not in url.lower(), timeout=60000)
                except Exception:
                    pass
            except Exception as e:
                try:
                    await page.screenshot(path="login_error.png")
                except: pass
                raise Exception(f"Login click failed or blocked: {str(e)}")

            if "login" in page.url.lower():
                raise Exception("Authentication failed. Portal remains on login screen after clicking button. Check credentials or site latency.")

            # ======================
            # 2. NAVIGATE TO COURSES
            # ======================
            try:
                # First wait for the sidebar to load and settle
                await asyncio.sleep(2)
                
                # Use the exact locator from the user's HTML snippet
                courses_locator = page.locator("li[ptooltip='Courses']").first
                await courses_locator.wait_for(state="visible", timeout=60000)
                # By default, Playwright waits for network idle after a click. 
                # On SPAs, this causes 30s timeouts if background trackers load slowly.
                await courses_locator.click(force=True, no_wait_after=True)
                
                # Wait for the courses page to physically render rather than networkidle
                await page.wait_for_selector("input[placeholder='Enter course name to search']", state="visible", timeout=60000)
            except Exception as e:
                raise Exception(f"Failed to navigate to courses page: {str(e)}")
                
            # ======================
            # 3. FIND AND SELECT THE COURSE
            # ======================
            try:
                # ==========================================
                # --- NEW FILTER CLEARING SEQUENCE ---
                # ==========================================
                
                # 1. Click the filter icon to open panel
                await page.wait_for_selector("span#filter-icon", state="visible", timeout=60000)
                await page.click("span#filter-icon")
                
                # 2. Wait for the overlay content to load
                overlay_selector = "div.ui-overlaypanel-content"
                await page.wait_for_selector(overlay_selector, state="visible", timeout=20000)
                
                # 3. Click the EXACT Clear button inside the active overlay
                clear_btn_selector = "div.ui-overlaypanel-content button.filterbtn1"
                await page.wait_for_selector(clear_btn_selector, state="visible", timeout=10000)
                await page.click(clear_btn_selector)
                
                # 4. Wait 1 second after clicking Clear
                await asyncio.sleep(1)
                # ==========================================

                # Search course
                search_input = "input[placeholder='Enter course name to search']"
                await page.wait_for_selector(search_input, state="visible")
                
                # --- NEW STEP BEFORE ENTERING COURSE NAME ---
                # 1. Click on the search input field to focus it
                await page.click(search_input)
                
                # 2. Select all existing text using Control+A (Meta+A on Mac, Control+A on Windows/Linux)
                import platform
                modifier = "Meta" if platform.system() == "Darwin" else "Control"
                await page.keyboard.press(f"{modifier}+A")
                
                # 3. Press Backspace to delete all selected text
                await page.keyboard.press("Backspace")
                
                # 4. Triple click the search input to make sure everything is selected
                await page.click(search_input, click_count=3)
                
                # 5. Press Backspace again to ensure the field is completely empty
                await page.keyboard.press("Backspace")
                
                # 6. Fill the field with empty string to fully reset it
                await page.fill(search_input, "")
                
                # 7. Wait half a second
                await asyncio.sleep(0.5)
                
                # 8. NOW type the course name into the search bar
                await page.type(search_input, course_name)
                
                # Click the search button provided by the user
                search_btn = page.locator("button:has(.icon-search)").first
                await search_btn.wait_for(state="visible", timeout=30000)
                await search_btn.click(no_wait_after=True)
                
                # Wait for search results by making sure the course name appears in the grid anywhere
                # We use a highly forgiving locator that just looks for the text inside any table cell or grid cell
                course_cell = page.locator(f"td:has-text('{course_name}'):visible, span:has-text('{course_name}'):visible, div.ui-table-wrapper :has-text('{course_name}'):visible").first
                await course_cell.wait_for(state="visible", timeout=60000)
                
                # Check the checkbox to select it
                await page.wait_for_selector("input#check_box_qb", state="visible")
                await page.click("input#check_box_qb")
                
                # Click Action dropdown using the provided label class/text
                action_label = page.locator("label.ui-dropdown-label:has-text('Action'), label.ui-dropdown-label").first
                await action_label.wait_for(state="visible", timeout=30000)
                await action_label.click()
                
                # Click the option inside dropdown: <li role="option" ... aria-label="Edit">
                edit_option = page.locator("li[aria-label='Edit'], li:has-text('Edit')").first
                await edit_option.wait_for(state="visible", timeout=30000)
                await edit_option.click(no_wait_after=True)
                
                # We do NOT use networkidle here because the page might naturally background-poll
            except Exception as e:
                try:
                    await page.screenshot(path="course_search_error.png")
                except: pass
                raise Exception(f"Error during Course search/selection for '{course_name}': {str(e)}")

            # ======================
            # 4. NAVIGATE TO MODULES AND SUBMODULES
            # ======================
            try:
                # Click tab wrapper: <a role="tab" ...><span class="...">Modules and Sub Modules</span></a>
                tab_locator = page.locator("a[role='tab']:has(span:has-text('Modules and Sub Modules')), span:has-text('Modules and Sub Modules')").first
                await tab_locator.wait_for(state="visible", timeout=30000)
                await tab_locator.click()
                
                # Find and select module using the provided span locator
                module_selector = page.locator(f"span.modulelist:has-text('{module_name}')").first
                await module_selector.wait_for(state="visible", timeout=10000)
                await module_selector.click()
                
                # Wait for items to load
                await asyncio.sleep(2)
            except Exception as e:
                try:
                    await page.screenshot(path="module_search_error.png")
                except: pass
                raise Exception(f"Error finding Module '{module_name}': {str(e)}")

            try:
                # Find the div with the test name content
                test_div = page.locator(f"div.content_test_name:has-text('{test_name}')").first
                await test_div.wait_for(state="visible", timeout=60000)
                
                # We need to find the parent row (tr) that contains this test name, then click the toggler in that row
                test_row = page.locator("tr").filter(has=test_div).first
                toggler = test_row.locator("span.ui-row-toggler, span.fa-chevron-circle-right").first
                
                await toggler.wait_for(state="visible", timeout=30000)
                await toggler.click(no_wait_after=True)
                
                # Slight wait for expansion content
                await asyncio.sleep(2)
            except Exception as e:
                raise Exception(f"Error finding Test '{test_name}': {str(e)}")

            # ======================
            # 6. EXPAND ALL 7 DROPDOWN SECTIONS
            # ======================
            sections = [
                "Test Control & Restrictions - Basic",
                "Results Control",
                "Programming Question Options",
                "Test Control & Restrictions - Advanced",
                "Manual Evaluation",
                "Choice based questions",
                "Section score cutoff restrictions"
            ]
            
            for section_name in sections:
                try:
                    # Dynamically find the accordion tab by matching its exact title text
                    target = page.locator(f"a[role='tab']:has(span.ui-accordion-header-text:has-text('{section_name}'))").first
                    await target.wait_for(state="visible", timeout=6000)
                    
                    expanded = await target.get_attribute("aria-expanded")
                    if expanded != "true":
                        await target.click(no_wait_after=True)
                        await asyncio.sleep(1) # Wait 1s for content to expand
                except Exception as e:
                    print(f"Warning: Could not expand section {section_name}: {e}")
                    
            # ======================
            # 7. SCRAPE CHECKED PARAMETERS
            # ======================
            try:
                # We will go through each section we intended to open, locate its expanded container, 
                # and extract ONLY the checked checkboxes.
                
                # Since the user didn't specify container mappings, we will find all checkboxes
                # and map them, or alternatively just grab all checkboxes on the page under the expanded sections.
                
                # Wait for checkboxes to be visible generally
                await page.wait_for_selector("p-checkbox", state="visible", timeout=10000)
                
                checkboxes = await page.locator("p-checkbox").all()
                
                for cb in checkboxes:
                    # Get checkbox div to check state
                    box_div = cb.locator("div.ui-chkbox-box").first
                    try:
                        classes = await box_div.get_attribute("class")
                        if not classes or "ui-state-active" not in classes:
                            continue # UNCHECKED -> Skip
                    except Exception:
                        continue 
                        
                    # It IS CHECKED. Get name
                    label = cb.locator("label.ui-chkbox-label").first
                    name = ""
                    try:
                        name = await label.inner_text()
                    except Exception:
                        pass
                        
                    if not name:
                        continue
                        
                    # Get any associated value (input/number/text nearby)
                    # We look within the parent row assuming typical PrimeNG structure
                    value = ""
                    try:
                        parent_row = cb.locator("xpath=./ancestor::div[contains(@class, 'ui-g') or contains(@class, 'row')]").first
                        val_input = parent_row.locator("input[type='text'], input[type='number']").first
                        if await val_input.count() > 0:
                            value = await val_input.input_value()
                    except Exception:
                        pass # Ignore if no value field exists
                        
                    # Determine section (Traverse up to accordion tab content or use heuristics)
                    # Since we don't have exact parent container selectors, we infer from previous logic.
                    # This is a best-effort section mapping.
                    section_assigned = "Test Control & Restrictions - Basic" # Default
                    
                    try:
                        # Grab the closest accordion tab or section header above it
                        accordion_header = cb.locator("xpath=./ancestor::div[contains(@class, 'ui-accordion-tab')]/preceding-sibling::div//a[contains(@class, 'ui-accordion-header')]").first
                        if await accordion_header.count() > 0:
                            header_text = await accordion_header.inner_text()
                            for sec_name in sections:
                                if sec_name.strip().lower() in header_text.lower():
                                    section_assigned = sec_name
                                    break
                    except Exception:
                        pass
                        
                    checked_parameters.append({
                        "section": section_assigned,
                        "name": name.strip(),
                        "value": value.strip() if value else ""
                    })

            except Exception as e:
                print(f"Error extracting parameters: {e}")

            return checked_parameters

        except Exception as e:
            # ======================
            # 9. ERROR HANDLING
            # ======================
            try:
                await page.screenshot(path="error_screenshot.png")
                print("Saved error screenshot to error_screenshot.png")
            except Exception:
                pass
            
            # Re-raise the exact exception 
            raise e
            
        finally:
            await browser.close()
