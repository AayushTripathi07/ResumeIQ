'use client';
import { useState } from 'react';
import UploadForm from '@/components/UploadForm';
import Dashboard from '@/components/Dashboard';

export default function Home() {
  const [resultData, setResultData] = useState<any>(null);

  return (
    <main className="min-h-screen bg-gray-50 text-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 tracking-tight mb-4">
            ResumeIQ
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            The AI-powered resume optimization engine. Match your profile against the JD, scrape your GitHub for perfect project highlighting, and export directly to LaTeX.
          </p>
        </div>

        {/* Dynamic Display state */}
        {!resultData ? (
          <UploadForm onComplete={(data) => setResultData(data)} />
        ) : (
          <div>
            <div className="mb-6 flex justify-center">
              <button 
                onClick={() => setResultData(null)}
                className="text-sm font-semibold text-blue-600 hover:text-blue-800 flex items-center transition"
              >
                &larr; Optimize Another Resume
              </button>
            </div>
            <Dashboard data={resultData} />
          </div>
        )}

      </div>
    </main>
  );
}
