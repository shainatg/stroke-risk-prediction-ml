import React from 'react';
import { Edit3, UploadCloud, Cpu, CheckCircle2, ArrowRight } from 'lucide-react';

export default function WorkflowSection() {
  const steps = [
    {
      step: "01",
      title: "Enter Text",
      description: "Type your query, question, or paragraph in the text input box.",
      icon: Edit3,
      color: "text-sky-600",
      bg: "bg-sky-50",
      border: "border-sky-200"
    },
    {
      step: "02",
      title: "Upload File",
      description: "Upload your PDF, Word (.docx), or plain text document.",
      icon: UploadCloud,
      color: "text-blue-600",
      bg: "bg-blue-50",
      border: "border-blue-200"
    },
    {
      step: "03",
      title: "Analyze Similarity",
      description: "Backend extracts paragraphs and computes TF-IDF cosine angles.",
      icon: Cpu,
      color: "text-indigo-600",
      bg: "bg-indigo-50",
      border: "border-indigo-200"
    },
    {
      step: "04",
      title: "Get Answer",
      description: "Instantly view the most relevant matching paragraph and exact score.",
      icon: CheckCircle2,
      color: "text-emerald-600",
      bg: "bg-emerald-50",
      border: "border-emerald-200"
    }
  ];

  return (
    <section className="w-full mt-14 pt-8 pb-12 border-t border-sky-100">
      <div className="max-w-5xl mx-auto">
        {/* Section Title */}
        <div className="text-center mb-8">
          <span className="text-xs font-bold text-sky-600 uppercase tracking-widest">
            Simple 4-Step Process
          </span>
          <h3 className="text-2xl font-bold text-slate-900 mt-1">
            How SmartMatch AI Works
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Enter Text &rarr; Upload File &rarr; Analyze Similarity &rarr; Get Answer
          </p>
        </div>

        {/* 4 Workflow Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 relative">
          {steps.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="card-soft rounded-2xl p-5 bg-white border border-sky-100 shadow-sm hover:shadow-md transition-all flex flex-col justify-between relative group"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className={`w-10 h-10 rounded-xl ${item.bg} border ${item.border} flex items-center justify-center ${item.color} shadow-xs`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-xs font-mono font-bold text-slate-300 group-hover:text-sky-500 transition-colors">
                      {item.step}
                    </span>
                  </div>

                  <h4 className="text-base font-bold text-slate-900 mb-1">
                    {item.title}
                  </h4>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    {item.description}
                  </p>
                </div>

                {/* Connecting arrow for larger screens */}
                {idx < steps.length - 1 && (
                  <div className="hidden lg:block absolute -right-3 top-1/2 -translate-y-1/2 z-10 text-slate-300">
                    <ArrowRight className="w-4 h-4 text-sky-300" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
