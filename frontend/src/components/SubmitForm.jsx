import React, { useState } from 'react';
import { UploadCloud, FileText, Link as LinkIcon, Zap, Loader2 } from 'lucide-react';

const DEMO_APPEALS = [
  {
    label: "Kerala Floods - Red Cross",
    color: "bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100",
    text: "URGENT: Kerala Floods Relief 2024. The Indian Red Cross Society is on the ground providing immediate assistance. Please donate to help families who have lost their homes. Bank: SBI, Acc: 123456789, IFSC: SBIN0001234. Or UPI: redcross@sbi. Every rupee counts! Check our updates at redcross.in"
  },
  {
    label: "Suspicious Medical Appeal",
    color: "bg-red-50 text-red-700 border-red-200 hover:bg-red-100",
    text: "Please help my brother!! He is in ICU after a terrible accident. We need 15 lakhs for his surgery immediately otherwise he will die. The hospital is asking for advance. Send money urgently to my personal UPI: randomguy@ybl. God will bless you. Pls share this with everyone!"
  },
  {
    label: "Verified NGO Campaign",
    color: "bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100",
    text: "Goonj Foundation - Assam Relief. We are collecting funds to distribute survival kits (ration, tarpaulins, hygiene items) to 5000 families in Majuli district. Our FCRA and 80G certificates are active. Donate securely via our official gateway at goonj.org/donate. Receipts will be sent within 24hrs."
  }
];

export default function SubmitForm({ onSubmit, loading }) {
  const [activeTab, setActiveTab] = useState('text');
  const [textVal, setTextVal] = useState('');
  const [linkVal, setLinkVal] = useState('');
  const [fileVal, setFileVal] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    
    if (activeTab === 'text') {
      formData.append('input_type', 'text');
      formData.append('text', textVal);
    } else if (activeTab === 'link') {
      formData.append('input_type', 'link');
      formData.append('url_link', linkVal);
    } else if (activeTab === 'screenshot') {
      formData.append('input_type', 'image');
      formData.append('image', fileVal);
    }
    onSubmit(formData);
  };

  const handleDemoClick = (text) => {
    setActiveTab('text');
    setTextVal(text);
  };

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-4 sm:p-5">
        <div className="flex items-center gap-2 mb-3">
          <Zap size={16} className="text-amber-500" />
          <h3 className="text-sm font-semibold text-slate-700">Try a Demo Appeal</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          {DEMO_APPEALS.map((demo, i) => (
            <button
              key={i}
              type="button"
              onClick={() => handleDemoClick(demo.text)}
              className={`text-left text-xs font-medium px-3 py-2.5 rounded-lg border transition-colors ${demo.color}`}
            >
              {demo.label}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="flex border-b border-slate-100">
          <button
            type="button"
            onClick={() => setActiveTab('text')}
            className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 ${activeTab === 'text' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-slate-500 hover:text-slate-700'}`}
          >
            <FileText size={16} /> Text
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('link')}
            className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 ${activeTab === 'link' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-slate-500 hover:text-slate-700'}`}
          >
            <LinkIcon size={16} /> Link
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('screenshot')}
            className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 ${activeTab === 'screenshot' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-slate-500 hover:text-slate-700'}`}
          >
            <UploadCloud size={16} /> Screenshot
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-4">
          {activeTab === 'text' && (
            <div>
              <textarea
                required
                rows="5"
                placeholder="Paste the appeal text here..."
                className="w-full p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none text-sm"
                value={textVal}
                onChange={(e) => setTextVal(e.target.value)}
              />
              <div className="text-right mt-1 text-xs text-slate-400">
                {textVal.length} characters
              </div>
            </div>
          )}
          
          {activeTab === 'link' && (
            <input
              type="url"
              required
              placeholder="https://example.com/appeal"
              className="w-full p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              value={linkVal}
              onChange={(e) => setLinkVal(e.target.value)}
            />
          )}

          {activeTab === 'screenshot' && (
            <div className="relative border-2 border-dashed border-slate-300 rounded-xl p-8 flex flex-col items-center justify-center text-slate-500 hover:border-blue-500 hover:bg-blue-50 transition-colors cursor-pointer">
              <UploadCloud size={32} className="mb-2" />
              <span className="text-sm">Drag and drop or click to upload</span>
              <input 
                type="file" 
                required
                accept="image/*"
                className="hidden" 
                id="file-upload"
                onChange={(e) => setFileVal(e.target.files[0])}
              />
              <label htmlFor="file-upload" className="absolute inset-0 cursor-pointer"></label>
              {fileVal && <span className="mt-2 text-blue-600 text-sm font-medium">{fileVal.name}</span>}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-xl transition-colors flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="spinner" size={20} /> Analyzing evidence...
              </>
            ) : (
              'Verify Appeal'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
