import { useCallback, useState } from 'react';
import { FaCloudUploadAlt, FaFileExcel, FaInfoCircle, FaDownload } from 'react-icons/fa';

export default function FileUpload({ file, setFile }) {
    const [isDragging, setIsDragging] = useState(false);

    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setIsDragging(true);
        } else if (e.type === 'dragleave') {
            setIsDragging(false);
        }
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const droppedFile = e.dataTransfer.files[0];
            if (droppedFile.name.endsWith('.csv') || droppedFile.name.endsWith('.xlsx')) {
                setFile(droppedFile);
            } else {
                alert('Please upload a .csv or .xlsx file');
            }
        }
    }, [setFile]);

    const handleChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const downloadTemplate = (e) => {
        e.preventDefault();
        const csvContent = "data:text/csv;charset=utf-8,course_name,module_name,test_name,output_filename\nSample_Course_123,Midterm_Exam,Document_1";
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "NeoExam_Template.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="glass-panel space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                    <span className="w-8 h-8 rounded-full bg-blue-accent/10 text-blue-accent flex items-center justify-center text-sm">2</span>
                    Exam Parameters
                </h2>

                <div className="flex items-center gap-3">
                    <button
                        onClick={downloadTemplate}
                        className="text-xs font-medium text-blue-accent bg-blue-50 border border-blue-200 hover:bg-blue-100 px-3 py-1.5 rounded-lg flex items-center gap-2 transition-colors"
                        title="Download sample CSV template"
                    >
                        <FaDownload size={12} />
                        Template
                    </button>
                    <div className="group relative">
                        <FaInfoCircle className="text-slate-400 hover:text-blue-accent cursor-pointer transition-colors" size={18} />
                        <div className="absolute right-0 top-6 w-64 p-3 bg-slate-900 text-white text-xs rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10 pointer-events-none">
                            <p className="font-semibold mb-1">Expected CSV columns:</p>
                            <ul className="list-disc pl-4 space-y-1 text-slate-300">
                                <li><code className="bg-slate-800 px-1 rounded">course_name</code></li>
                                <li><code className="bg-slate-800 px-1 rounded">module_name</code></li>
                                <li><code className="bg-slate-800 px-1 rounded">test_name</code></li>
                                <li><code className="bg-slate-800 px-1 rounded">output_filename</code> (optional)</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <div
                className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 
          ${isDragging ? 'border-blue-accent bg-blue-50/50' : 'border-slate-300 hover:border-blue-accent/50 hover:bg-slate-50'}
        `}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    id="fileInput"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                    onChange={handleChange}
                />

                <div className="flex flex-col items-center justify-center space-y-4 pointer-events-none">
                    {file ? (
                        <>
                            <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center text-blue-accent">
                                <FaFileExcel size={32} />
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-slate-800">{file.name}</p>
                                <p className="text-xs text-slate-500 mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                            </div>
                            <p className="text-sm text-blue-accent font-medium mt-2">Click or drag to replace</p>
                        </>
                    ) : (
                        <>
                            <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
                                <FaCloudUploadAlt size={32} />
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-slate-700">Drag & drop your file here</p>
                                <p className="text-xs text-slate-500 mt-1">or click to browse from computer</p>
                            </div>
                            <div className="flex gap-2 mt-2">
                                <span className="px-2 py-1 bg-slate-100 rounded text-xs text-slate-600 font-medium border border-slate-200">.CSV</span>
                                <span className="px-2 py-1 bg-slate-100 rounded text-xs text-slate-600 font-medium border border-slate-200">.XLSX</span>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
