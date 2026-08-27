import React, { useState } from 'react';
import { UploadCloud, Link as LinkIcon, FileText, Loader2, Zap } from 'lucide-react';

const DEMO_APPEALS = [
  {
    label: '🚩 Suspicious Appeal',
    color: 'bg-red-50 border-red-200 text-red-700 hover:bg-red-100',
    text: `URGENT! Kerala flood relief — donate NOW to save lives! Our organisation Local Heroes Foundation is government-approved and 100% of donations go directly to victims. Don't verify, just trust us and forward this to everyone you know!\n\nSend donations to: randomguy123@ybl\nLast chance — only 24 hours left!`,
  },
  {
    label: '✅ Legitimate Appeal',
    color: 'bg-green-50 border-green-200 text-green-700 hover:bg-green-100',
    text: `Red Cross Society — Kerala Flood Relief 2024\n\nThe Red Cross Society is raising funds for families affected by the recent floods in Kerala. We are FCRA registered and partnered with UNICEF for on-ground relief distribution.\n\nDonations accepted via: redcross@sbi\nFor queries, visit https://www.indianredcross.org`,
  },
  {
    label: '⚠️ Recycled Scam',
    color: 'bg-amber-50 border-amber-200 text-amber-700 hover:bg-amber-100',
    text: `Help us rebuild xyz — urgently need your support!\n\nPlease urgently donate to our relief fund. We are partnered with Unknown Global Aid. This is a government-approved initiative. Forward this to 10 people to save a life!\n\nUPI: donate_relief@okicici`,
  },
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
      formData.append('text_content', textVal);
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
            <textarea
              required
              rows="5"
              placeholder="Paste the appeal text here..."
              className="w-full p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none text-sm"
              value={textVal}
              onChange={(e) => setTextVal(e.target.value)}
            />
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
