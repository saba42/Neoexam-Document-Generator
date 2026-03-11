import { FaCheckCircle, FaSpinner, FaCircle } from 'react-icons/fa';

export default function StatusTracker({ currentStep, error }) {
    const steps = [
        'Connecting to portal',
        'Logging in',
        'Navigating to course',
        'Reading parameters',
        'Building document',
        'Done!'
    ];

    return (
        <div className="glass-panel space-y-6">
            <h2 className="text-xl font-bold text-slate-900">Generation Progress</h2>
            <div className="relative pl-4">
                {/* Vertical line connecting steps */}
                <div className="absolute left-[1.3rem] top-3 bottom-6 w-0.5 bg-slate-200"></div>

                <ul className="space-y-6 relative z-10">
                    {steps.map((step, index) => {
                        const stepNum = index + 1;
                        const isCompleted = currentStep > stepNum && (!error || currentStep > stepNum);
                        const isCurrent = currentStep === stepNum;
                        const isError = error && currentStep === stepNum;

                        return (
                            <li key={step} className="flex items-start gap-4">
                                <div className="flex-shrink-0 mt-0.5 relative bg-slate-50">
                                    {isCompleted ? (
                                        <FaCheckCircle className="text-blue-accent w-5 h-5 relative z-10 bg-white rounded-full" />
                                    ) : isCurrent ? (
                                        isError ? (
                                            <div className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center relative z-10 ring-4 ring-white">
                                                <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
                                            </div>
                                        ) : (
                                            <div className="relative z-10 bg-white rounded-full">
                                                <FaSpinner className="text-blue-accent w-5 h-5 animate-spin-slow" />
                                                <div className="absolute inset-0 rounded-full animate-pulse-ring"></div>
                                            </div>
                                        )
                                    ) : (
                                        <FaCircle className={`w-5 h-5 relative z-10 bg-white rounded-full ${isError ? 'text-slate-200' : 'text-slate-300'}`} />
                                    )}
                                </div>
                                <div className="flex-1">
                                    <p className={`font-medium ${isCompleted ? 'text-slate-800' :
                                        isCurrent ? (isError ? 'text-red-600' : 'text-blue-accent') :
                                            'text-slate-400'
                                        }`}>
                                        {step}
                                    </p>
                                    {isError && (
                                        <p className="text-sm text-red-500 mt-1">{error}</p>
                                    )}
                                </div>
                            </li>
                        );
                    })}
                </ul>
            </div>
        </div>
    );
}
