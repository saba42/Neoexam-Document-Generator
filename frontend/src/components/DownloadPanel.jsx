import { FaFileDownload, FaCheckCircle, FaExclamationTriangle, FaArchive } from 'react-icons/fa';

export default function DownloadPanel({ jobId, filename, isZip, error, reset }) {
    if (!jobId && !error) return null;

    const handleDownloadDocx = () => {
        const BASE = import.meta.env.VITE_API_URL || "";
        const url = `${BASE}/api/download/docx/${jobId}?filename=${encodeURIComponent(filename)}`;
        window.location.href = url;
    };

    return (
        <div className={`glass-panel border-2 ${error ? 'border-red-200 bg-red-50/50' : 'border-green-200 bg-green-50/50'}`}>
            <div className="flex flex-col items-center justify-center text-center space-y-4 py-6">
                {error ? (
                    <>
                        <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center text-red-500">
                            <FaExclamationTriangle size={32} />
                        </div>
                        <h2 className="text-2xl font-bold text-red-700">Generation Failed</h2>
                        <p className="text-red-600 max-w-md whitespace-pre-wrap text-left text-sm bg-red-50 p-4 rounded-lg border border-red-100 mt-2">
                            {typeof error === 'object' ? (error.message || JSON.stringify(error)) : String(error)}
                        </p>
                        <button onClick={reset} className="mt-4 px-8 py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl shadow-lg hover:shadow-red-600/25 transform hover:-translate-y-0.5 transition-all duration-200">
                            Try Again
                        </button>
                    </>
                ) : (
                    <>
                        <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center text-green-500">
                            <FaCheckCircle size={32} />
                        </div>
                        <h2 className="text-2xl font-bold text-green-700">Document Ready!</h2>
                        <p className="text-green-600 mb-2">Your exam parameters document has been generated successfully.</p>

                        <button
                            onClick={handleDownloadDocx}
                            className="mt-4 px-8 py-4 bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl shadow-lg hover:shadow-green-600/25 transform hover:-translate-y-0.5 transition-all duration-200 flex items-center gap-3 cursor-pointer"
                        >
                            {isZip ? <FaArchive size={22} /> : <FaFileDownload size={22} />}
                            Download {isZip ? '.zip' : '.docx'}
                        </button>

                        <button onClick={reset} className="text-sm font-semibold text-green-700 hover:text-green-800 hover:underline mt-4 cursor-pointer">
                            Generate another document
                        </button>
                    </>
                )}
            </div>
        </div>
    );
}
