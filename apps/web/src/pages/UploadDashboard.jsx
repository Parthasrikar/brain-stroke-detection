import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, Activity, Brain, AlertTriangle, CheckCircle, FileText, History, LogOut, ChevronRight, Stethoscope } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { predictScan, getHistory, getMe } from '../api';
import Chatbot from '../components/Chatbot';

const UploadDashboard = () => {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [user, setUser] = useState(null);
    const [history, setHistory] = useState([]);
    const [showHistory, setShowHistory] = useState(false);
    const fileInputRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/auth');
            return;
        }
        fetchUserData();
    }, []);

    const fetchUserData = async () => {
        try {
            const userData = await getMe();
            setUser(userData);
            const historyData = await getHistory();
            setHistory(historyData);
        } catch (err) {
            localStorage.removeItem('token');
            navigate('/auth');
        }
    };

    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
            setResult(null);
            setError(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);

        try {
            const data = await predictScan(file);
            if (data.error) {
                setError(data.error);
                setResult(null);
            } else {
                setResult(data);
                // Refresh history
                const updatedHistory = await getHistory();
                setHistory(updatedHistory);
            }
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to process image. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/auth');
    };

    const clearFile = () => {
        setFile(null);
        setPreview(null);
        setResult(null);
        setError(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
    };

    return (
        <div className="min-h-screen pt-24 pb-12 px-4 bg-dark text-white relative">
            <Chatbot context={result ? `Status: ${result.status}. Prediction: ${result.prediction}. Advice: ${result.advice}` : ''} />

            <div className="max-w-6xl mx-auto">
                {/* Navbar Action */}
                <div className="flex justify-between items-center mb-10">
                    <div>
                        <h1 className="text-3xl font-bold">Analysis Dashboard</h1>
                        <p className="text-slate-400">Welcome, {user?.full_name || 'User'}</p>
                    </div>
                    <div className="flex gap-4">
                        <button
                            onClick={() => setShowHistory(!showHistory)}
                            className="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg flex items-center gap-2 transition-all"
                        >
                            <History className="w-4 h-4" /> {showHistory ? 'Close History' : 'View History'}
                        </button>
                        <button
                            onClick={handleLogout}
                            className="text-slate-400 hover:text-red-400 p-2 transition-colors"
                        >
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                    {/* Left & Center: Upload & Main Analysis */}
                    <div className={`lg:col-span-2 space-y-8 ${showHistory ? 'hidden lg:block' : ''}`}>
                        <div className="grid md:grid-cols-2 gap-8">
                            <div className="space-y-6">
                                <div
                                    className={`border-2 border-dashed rounded-2x p-8 flex flex-col items-center justify-center transition-all h-80 ${preview ? 'border-primary/50 bg-slate-900/50' : 'border-slate-700 hover:border-primary/50 hover:bg-slate-800/50'}`}
                                    onDragOver={(e) => e.preventDefault()}
                                    onDrop={(e) => {
                                        e.preventDefault();
                                        const selected = e.dataTransfer.files[0];
                                        if (selected) {
                                            setFile(selected);
                                            setPreview(URL.createObjectURL(selected));
                                        }
                                    }}
                                >
                                    <AnimatePresence mode="wait">
                                        {preview ? (
                                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="relative w-full h-full flex flex-col items-center">
                                                <img src={preview} alt="Preview" className="max-h-full max-w-full rounded-lg shadow-lg object-contain" />
                                                <button onClick={clearFile} className="absolute -top-2 -right-2 p-1 bg-red-500 rounded-full text-white hover:bg-red-600">
                                                    <X className="w-4 h-4" />
                                                </button>
                                            </motion.div>
                                        ) : (
                                            <div className="text-center">
                                                <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4 text-primary">
                                                    <Upload className="w-8 h-8" />
                                                </div>
                                                <p className="text-lg font-medium mb-1">Upload CT Scan</p>
                                                <p className="text-sm text-slate-500 mb-4">Drag and drop or browse</p>
                                                <button onClick={() => fileInputRef.current?.click()} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm border border-slate-700">Select File</button>
                                            </div>
                                        )}
                                    </AnimatePresence>
                                    <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept="image/*" />
                                </div>

                                <button
                                    onClick={handleUpload}
                                    disabled={!file || loading}
                                    className={`w-full py-4 rounded-xl font-bold text-lg shadow-lg transition-all flex items-center justify-center gap-2 ${!file || loading ? 'bg-slate-800 text-slate-500 cursor-not-allowed' : 'bg-gradient-to-r from-primary to-indigo-600 text-white'}`}
                                >
                                    {loading ? <Activity className="w-5 h-5 animate-spin" /> : <Brain className="w-5 h-5" />}
                                    {loading ? 'Analyzing...' : 'Analyze Scan'}
                                </button>

                                {error && (
                                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex gap-3">
                                        <AlertTriangle className="w-5 h-5 text-red-500 shrink-0" />
                                        <p className="text-sm text-red-200">{error}</p>
                                    </motion.div>
                                )}
                            </div>

                            {/* Analysis Result */}
                            <div className="relative">
                                <AnimatePresence>
                                    {result ? (
                                        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="bg-card border border-slate-700 rounded-2xl h-full shadow-2xl relative overflow-hidden flex flex-col">
                                            <div className={`absolute top-0 left-0 w-2 h-full ${result.prediction === 'Normal' ? 'bg-green-500' : 'bg-red-500'}`}></div>

                                            {/* Scrollable Content Area */}
                                            <div className="flex-1 overflow-y-auto p-6 ml-2 space-y-6 scrollbar-thin scrollbar-thumb-slate-700 max-h-[600px]">
                                                {/* Header */}
                                                <div>
                                                    <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Diagnosis</h2>
                                                    <div className="flex items-baseline gap-2">
                                                        <h3 className={`text-3xl font-bold ${result.prediction === 'Normal' ? 'text-green-400' : 'text-red-400'}`}>{result.status}</h3>
                                                        <span className="text-lg text-slate-500">{(result.confidence * 100).toFixed(2)}%</span>
                                                    </div>
                                                </div>

                                                <div className="space-y-4">
                                                    {/* Prediction Details */}
                                                    <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                                                        <div className="flex items-center gap-2 mb-2 text-primary">
                                                            <Brain className="w-4 h-4" />
                                                            <span className="text-sm font-semibold">Predicted Class</span>
                                                        </div>
                                                        <div className="text-sm text-slate-300">
                                                            <p className="mb-3"><strong>{result.prediction}</strong> (Confidence: {(result.confidence * 100).toFixed(2)}%)</p>
                                                            <div className="space-y-1 text-xs">
                                                                {Object.entries(result.probabilities).map(([className, prob]) => (
                                                                    <div key={className} className="flex justify-between">
                                                                        <span className="text-slate-400">{className}:</span>
                                                                        <span className="text-slate-300">{(prob * 100).toFixed(2)}%</span>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* Medical Advice */}
                                                    <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                                                        <div className="flex items-center gap-2 mb-2 text-secondary">
                                                            <AlertTriangle className="w-4 h-4" />
                                                            <span className="text-sm font-semibold">Medical Advice</span>
                                                        </div>
                                                        <p className="text-sm text-slate-300 leading-relaxed">{result.advice}</p>
                                                    </div>

                                                    {/* Additional Suggestion */}
                                                    {result.suggestion && (
                                                        <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                                                            <div className="flex items-center gap-2 mb-2 text-slate-400">
                                                                <FileText className="w-4 h-4" />
                                                                <span className="text-sm font-semibold">Suggestion</span>
                                                            </div>
                                                            <p className="text-sm text-slate-300">{result.suggestion}</p>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </motion.div>
                                    ) : (
                                        <div className="h-full flex flex-col items-center justify-center text-slate-600 border border-slate-800 rounded-2xl bg-slate-900/20 p-8 text-center">
                                            <Brain className="w-16 h-16 mb-4 opacity-10" />
                                            <p className="text-sm">Upload and analyze to see results</p>
                                        </div>
                                    )}
                                </AnimatePresence>
                            </div>
                        </div>
                    </div>

                    {/* History Sidebar */}
                    <div className={`${showHistory ? 'block' : 'hidden lg:block'} lg:col-span-1`}>
                        <div className="bg-card border border-slate-700 rounded-2xl p-6 h-[calc(100vh-250px)] lg:h-[600px] flex flex-col shadow-xl">
                            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                                <History className="w-5 h-5 text-primary" /> Past Scans
                            </h2>
                            <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-thin scrollbar-thumb-slate-700">
                                {history.length === 0 ? (
                                    <div className="text-center py-10 text-slate-500 text-sm italic">No scan history found</div>
                                ) : (
                                    history.map((item, idx) => (
                                        <div
                                            key={item._id || idx}
                                            onClick={() => {
                                                setResult(item.prediction_result);
                                                if (item.image_path) {
                                                    // Use BASE_URL/uploads path if it's a relative path from API
                                                    const imgUrl = item.image_path.startsWith('http')
                                                        ? item.image_path
                                                        : `${BASE_URL}${item.image_path}`;
                                                    setPreview(imgUrl);
                                                }
                                                setShowHistory(false);
                                            }}
                                            className="p-3 bg-slate-800/40 border border-slate-700/50 rounded-xl hover:bg-slate-800 transition-colors cursor-pointer group"
                                        >
                                            <div className="flex justify-between items-start mb-1">
                                                <span className={`text-xs font-bold px-2 py-0.5 rounded ${item.prediction_result.prediction === 'Normal' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                                                    {item.prediction_result.prediction}
                                                </span>
                                                <span className="text-[10px] text-slate-500">{new Date(item.created_at).toLocaleDateString()}</span>
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <span className="text-xs text-slate-400 truncate max-w-[120px]">{item.filename}</span>
                                                <ChevronRight className="w-3 h-3 text-slate-600 group-hover:text-primary transition-colors" />
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UploadDashboard;
