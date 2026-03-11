import { useState, useRef, useEffect } from 'react';
import CredentialsForm from './components/CredentialsForm';
import FileUpload from './components/FileUpload';
import StatusTracker from './components/StatusTracker';
import DownloadPanel from './components/DownloadPanel';
import { FaCog, FaPaperPlane } from 'react-icons/fa';

export default function App() {
  const BASE = import.meta.env.VITE_API_URL || "";
  const [portalUrl, setPortalUrl] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [file, setFile] = useState(null);

  const [isGenerating, setIsGenerating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [filename, setFilename] = useState(null);
  const [isZip, setIsZip] = useState(false);

  const eventSourceRef = useRef(null);

  const canGenerate = portalUrl && email && password && file && !isGenerating;

  const handleGenerate = async () => {
    if (!canGenerate) return;

    setIsGenerating(true);
    setCurrentStep(1);
    setError(null);
    setJobId(null);
    setFilename(null);
    setIsZip(false);

    // Setup SSE connection to listen for progress
    eventSourceRef.current = new EventSource(`${BASE}/status`);

    eventSourceRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.step) setCurrentStep(data.step);
        if (data.status === 'error' || data.error) {
          setError(data.message || data.error || 'An unknown error occurred');
          setIsGenerating(false);
          eventSourceRef.current?.close();
        }
      } catch (err) {
        console.error('Failed to parse SSE data', err);
      }
    };

    eventSourceRef.current.onerror = () => {
      // Typically EventSource retries automatically, but we can log it.
      console.warn('SSE Connection Error or Closed');
    };

    try {
      const formData = new FormData();
      formData.append('portal_url', portalUrl);
      formData.append('email', email);
      formData.append('password', password);
      formData.append('file', file);

      const response = await fetch(`${BASE}/generate`, {
        method: 'POST',
        body: formData,
      });

      const rawText = await response.text();
      let json;
      try {
        json = JSON.parse(rawText);
      } catch (e) {
        // If the response is not valid JSON (e.g., Render 502/504 HTML error page)
        throw new Error(`Server returned ${response.status}: ${rawText.substring(0, 100)}...`);
      }

      if (!response.ok || json.status === 'error') {
        throw new Error(json.message || json.detail || `Server returned ${response.status}`);
      }

      setJobId(json.job_id);
      setFilename(json.filename);
      setIsZip(json.is_zip);

      setCurrentStep(6);
      setIsGenerating(false);
    } catch (err) {
      setError(err.message || 'Failed to connect to server');
      setIsGenerating(false);
    } finally {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    }
  };

  const handleReset = () => {
    setCurrentStep(0);
    setError(null);
    setJobId(null);
    setFilename(null);
    setIsZip(false);
    setFile(null);
    setIsGenerating(false);
  };

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-slate-200 py-4 fixed w-full top-0 z-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center shadow-lg shadow-slate-900/20">
              <FaCog className="text-white w-4 h-4 animate-spin-slow" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              NeoExam <span className="text-slate-400 font-medium">| Document Generator</span>
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl pt-32 pb-10">
        <div className="flex flex-col lg:flex-row gap-8 items-start">

          {/* Left Column - Inputs */}
          <div className="w-full lg:w-3/5 space-y-6">
            {!jobId && !error ? (
              <>
                <CredentialsForm
                  portalUrl={portalUrl} setPortalUrl={setPortalUrl}
                  email={email} setEmail={setEmail}
                  password={password} setPassword={setPassword}
                />

                <FileUpload file={file} setFile={setFile} />

                <button
                  onClick={handleGenerate}
                  disabled={!canGenerate}
                  className="btn-primary"
                >
                  {isGenerating ? (
                    <>
                      <FaCog className="animate-spin w-5 h-5" />
                      Generating Document...
                    </>
                  ) : (
                    <>
                      <FaPaperPlane className="w-5 h-5" />
                      Generate Document
                    </>
                  )}
                </button>
              </>
            ) : (
              <DownloadPanel
                jobId={jobId}
                filename={filename}
                isZip={isZip}
                error={error}
                reset={handleReset}
              />
            )}
          </div>

          {/* Right Column - Status Tracker */}
          <div className="w-full lg:w-2/5 lg:sticky lg:top-32">
            <StatusTracker currentStep={currentStep} error={error} />
          </div>

        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 mt-auto relative z-10 w-full">
        <div className="container mx-auto px-4 text-center text-slate-400 font-medium text-sm">
          NeoExam © {new Date().getFullYear()} • v1.1
        </div>
      </footer>
    </div>
  );
}
