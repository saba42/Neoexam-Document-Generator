import { useState } from 'react';
import { FaEye, FaEyeSlash } from 'react-icons/fa';

export default function CredentialsForm({ portalUrl, setPortalUrl, email, setEmail, password, setPassword }) {
    const [showPassword, setShowPassword] = useState(false);

    return (
        <div className="glass-panel space-y-6">
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                <span className="w-8 h-8 rounded-full bg-blue-accent/10 text-blue-accent flex items-center justify-center text-sm">1</span>
                Portal Credentials
            </h2>

            <div className="space-y-4">
                <div className="input-group">
                    <label className="input-label" htmlFor="portalUrl">Portal URL</label>
                    <input
                        id="portalUrl"
                        type="url"
                        placeholder="https://your-portal.example.com"
                        className="input-field"
                        value={portalUrl}
                        onChange={(e) => setPortalUrl(e.target.value)}
                    />
                </div>

                <div className="input-group">
                    <label className="input-label" htmlFor="email">Email</label>
                    <input
                        id="email"
                        type="email"
                        placeholder="admin@example.com"
                        className="input-field"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                </div>

                <div className="input-group">
                    <label className="input-label" htmlFor="password">Password</label>
                    <div className="relative">
                        <input
                            id="password"
                            type={showPassword ? 'text' : 'password'}
                            placeholder="••••••••"
                            className="input-field pr-12"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                        <button
                            type="button"
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-blue-accent transition-colors"
                            onClick={() => setShowPassword(!showPassword)}
                        >
                            {showPassword ? <FaEyeSlash size={18} /> : <FaEye size={18} />}
                        </button>
                    </div>
                </div>
            </div>

            <p className="text-xs text-slate-500 mt-4 flex items-center gap-1.5">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                Your credentials are never stored.
            </p>
        </div>
    );
}
