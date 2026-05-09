'use client';
import { useState, useEffect } from 'react';
import DiffViewer from '@/components/DiffViewer';

export default function Dashboard({ data }: { data: any }) {
  const [activeTab, setActiveTab] = useState<'SCORE' | 'DIFF' | 'VISUAL'>('SCORE');
  const [pdfBlobUrl, setPdfBlobUrl] = useState<string>('');

  // Dynamically fetch and generate the Blob streaming URL for the Visual Frame bypassing URL GET constraints!
  useEffect(() => {
    if (activeTab === 'VISUAL' && data.latex_code && !pdfBlobUrl) {
      const generatePreview = async () => {
        try {
          const formData = new FormData();
          formData.append('latex_code', data.latex_code);
          const res = await fetch("http://localhost:8000/api/process/compile", {
            method: "POST",
            body: formData,
          });
          if (res.ok) {
            const blob = await res.blob();
            setPdfBlobUrl(URL.createObjectURL(blob));
          }
        } catch (e) {
          console.error("Failed to generate PDF overlay stream", e);
        }
      };
      generatePreview();
    }
  }, [activeTab, data.latex_code, pdfBlobUrl]);

  return (
    <div className="w-full max-w-6xl mx-auto mt-8 bg-white shadow-xl rounded-xl overflow-hidden border border-gray-200">
      
      {/* Dashboard Header / Persistent Actions */}
      <div className="bg-gray-50 flex justify-between items-center p-6 border-b border-gray-200">
        <div>
          <h2 className="text-2xl font-extrabold text-gray-800">Optimization Results</h2>
          <p className="text-sm text-gray-500 mt-1">Review your AI-enhanced profile before exporting.</p>
        </div>
        <div className="flex space-x-3">
          
          <form method="POST" action="http://localhost:8000/api/process/compile" target="_blank" className="inline-block">
            <input type="hidden" name="latex_code" value={data.latex_code || ''} />
            <button type="submit" className="font-semibold text-gray-700 bg-white border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-100 transition shadow-sm">
              📄 Download Compiled PDF
            </button>
          </form>

          <form method="POST" action="https://www.overleaf.com/docs" target="_blank" className="inline-block">
            <input type="hidden" name="snip" value={data.latex_code || ''} />
            <button type="submit" className="font-semibold text-white bg-green-600 px-4 py-2 rounded-lg hover:bg-green-700 transition shadow-sm">
              ✏️ Open in Overleaf
            </button>
          </form>
          
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-200 bg-gray-50/50">
        <button 
          onClick={() => setActiveTab('SCORE')}
          className={`flex-1 py-4 text-center text-sm font-bold tracking-wide transition ${
            activeTab === 'SCORE' ? 'bg-white text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-800'
          }`}
        >
          ATS SCORE ANALYSIS
        </button>
        <button 
          onClick={() => setActiveTab('DIFF')}
          className={`flex-1 py-4 text-center text-sm font-bold tracking-wide transition ${
            activeTab === 'DIFF' ? 'bg-white text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-800'
          }`}
        >
          CONTENT DIFF
        </button>
        <button 
          onClick={() => setActiveTab('VISUAL')}
          className={`flex-1 py-4 text-center text-sm font-bold tracking-wide transition ${
            activeTab === 'VISUAL' ? 'bg-white text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-800'
          }`}
        >
          VISUAL PDF DIFF
        </button>
      </div>

      {/* Tab Content Panels */}
      <div className="p-8 min-h-[500px]">
        {activeTab === 'SCORE' && (
          <div className="flex flex-col items-center justify-center space-y-6 pt-10">
            <h3 className="text-xl font-medium text-gray-700 mb-4">Sentence-Transformer Mathematical Match</h3>
            <div className="grid grid-cols-2 gap-12 text-center w-full max-w-xl">
              <div className="bg-red-50 p-6 rounded-2xl shadow-inner border border-red-100">
                <p className="text-gray-500 font-semibold mb-2 uppercase tracking-widest text-xs">Original Cosine Match</p>
                <p className="text-6xl font-black text-red-500">{data.before_score}</p>
              </div>
              <div className="bg-green-50 p-6 rounded-2xl shadow-inner border border-green-100 relative overflow-hidden">
                <div className="absolute top-0 right-0 bg-green-200 text-green-800 text-xs px-2 py-1 rounded-bl-lg font-bold">Optimized</div>
                <p className="text-gray-500 font-semibold mb-2 uppercase tracking-widest text-xs">ResumeIQ Score</p>
                <p className="text-6xl font-black text-green-600">{data.after_score}</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'DIFF' && (
          <div className="space-y-6">
             <DiffViewer diffs={data.diffs} />
          </div>
        )}

        {activeTab === 'VISUAL' && (
          <div className="flex flex-col md:flex-row space-y-6 md:space-y-0 md:space-x-6 h-[700px]">
            <div className="flex-1 border border-gray-300 rounded-xl overflow-hidden bg-gray-100 flex flex-col">
              <div className="bg-gray-200 p-3 text-center text-sm font-bold text-gray-700 uppercase tracking-widest border-b border-gray-300">
                Original Upload
              </div>
              {data.original_pdf_url ? (
                  <iframe src={data.original_pdf_url} className="w-full h-full border-none bg-white" title="Original PDF" />
              ) : (
                  <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-gray-500">
                    <span className="text-4xl mb-4">📄</span>
                    <p className="font-semibold mb-2">Original Document Base Linked</p>
                    <p className="text-sm px-6">Your exact PDF metadata remains the structural baseline for your visual output.</p>
                  </div>
              )}
            </div>
            
            <div className="flex-1 border border-green-300 shadow-xl shadow-green-900/10 rounded-xl overflow-hidden bg-white flex flex-col relative w-full">
               <div className="bg-gradient-to-r from-green-50 to-green-100 p-3 text-center text-sm font-bold text-green-800 uppercase tracking-widest border-b border-green-200">
                 Optimized Result
               </div>
               {pdfBlobUrl ? (
                 <iframe src={pdfBlobUrl} className="w-full h-full border-none" title="Optimized PDF Result" />
               ) : (
                 <div className="flex flex-col items-center justify-center h-full text-gray-400 space-y-4">
                    <span className="text-xl">⚙️ generating native visual overlay...</span>
                 </div>
               )}
            </div>
          </div>
        )}
      </div>

    </div>
  );
}
