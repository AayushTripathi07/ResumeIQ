'use client';
import { useState } from 'react';

export default function UploadForm({ onComplete }: { onComplete: (data: any) => void }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // Build FormData directly from the form elements
      const formData = new FormData(e.currentTarget);
      
      // Capture the original PDF file locally so we can preview it on the dashboard!
      const file = formData.get("resume");
      let originalUrl = "";
      if (file && file instanceof File) {
          originalUrl = URL.createObjectURL(file);
      }
      
      // Ping the FastAPI backend
      const response = await fetch("http://localhost:8000/api/process/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to process resume pipeline. Check if backend is running.");
      }

      const data = await response.json();
      data.original_pdf_url = originalUrl;
      onComplete(data);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow-lg border border-gray-100 max-w-2xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-gray-800 border-b pb-2">Optimize Your Resume</h2>
      
      {error && <div className="text-red-500 text-sm font-semibold p-3 bg-red-50 rounded-lg">{error}</div>}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Resume (PDF)</label>
        <input name="resume" type="file" accept=".pdf" required className="w-full border border-gray-300 rounded-lg p-2 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Job Description</label>
        <textarea name="job_description" required rows={4} className="w-full border border-gray-300 rounded-lg p-3 outline-none focus:ring-2 focus:ring-blue-500" placeholder="Paste the target JD here..."></textarea>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">GitHub Profile Link</label>
        <input name="github_url" type="url" className="w-full border border-gray-300 rounded-lg p-3 outline-none focus:ring-2 focus:ring-blue-500" placeholder="https://github.com/username" />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Additional Information (Optional)</label>
        <textarea name="additional_info" rows={2} className="w-full border border-gray-300 rounded-lg p-3 outline-none focus:ring-2 focus:ring-blue-500" placeholder="Anything else you'd want the AI to include..."></textarea>
      </div>

      <button disabled={loading} type="submit" className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 transition disabled:opacity-50">
        {loading ? 'Processing through ResumeIQ Engine...' : 'Optimize Now'}
      </button>
    </form>
  );
}
