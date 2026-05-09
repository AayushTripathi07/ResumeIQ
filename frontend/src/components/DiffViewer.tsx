'use client';

export default function DiffViewer({ diffs }: { diffs: any[] }) {
  return (
    <div className="space-y-8">
      {diffs.map((diff, idx) => (
        <div key={idx} className="border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          <div className="bg-gray-100 text-gray-800 font-bold px-4 py-2 border-b border-gray-200 uppercase text-xs tracking-wider">
            Section: {diff.section}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-gray-200">
            {/* Before */}
            <div className="p-5 bg-red-50/30">
              <span className="text-xs font-bold text-red-600 uppercase tracking-widest mb-2 block">Original Text</span>
              <p className="text-gray-700 strike line-through opacity-70">{diff.before}</p>
            </div>
            {/* After */}
            <div className="p-5 bg-green-50/50">
               <span className="text-xs font-bold text-green-700 uppercase tracking-widest mb-2 block">AI Enhanced</span>
               <p className="text-gray-900 font-medium">{diff.after}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
