import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight, Brain, ShieldCheck, Activity } from 'lucide-react';

const Landing = () => {
    return (
        <div className="min-h-screen pt-20 bg-dark text-white overflow-hidden relative">
            {/* Background Gradients */}
            <div className="absolute top-0 left-0 w-96 h-96 bg-primary/20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
            <div className="absolute bottom-0 right-0 w-96 h-96 bg-secondary/20 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

            <div className="max-w-screen-xl mx-auto px-4 py-16 lg:py-24 grid lg:grid-cols-2 gap-12 items-center">
                {/* Left Content */}
                <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <div className="inline-flex items-center px-3 py-1 rounded-full border border-primary/30 bg-primary/10 text-primary text-sm font-medium mb-6">
                        <span className="flex w-2 h-2 bg-primary rounded-full mr-2 animate-pulse"></span>
                        AI-Powered Diagnostics
                    </div>
                    <h1 className="text-5xl lg:text-7xl font-bold leading-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">
                        Advanced Stroke <br />
                        <span className="text-primary">Detection</span> System
                    </h1>
                    <p className="text-lg text-slate-400 mb-8 max-w-lg">
                        Utilizing Hierarchical Deep Learning (ResNet50) to detect Ischemic and Haemorrhagic strokes from CT scans with high precision. Instant analysis, personalized rehabilitation support.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4">
                        <Link to="/auth">
                            <button className="px-8 py-4 bg-primary hover:bg-primary/90 rounded-xl font-semibold text-white shadow-lg shadow-primary/25 transition-all flex items-center justify-center gap-2 group w-full sm:w-auto">
                                Start Diagnosis
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </button>
                        </Link>
                        <button className="px-8 py-4 bg-slate-800 hover:bg-slate-700/80 rounded-xl font-semibold text-white border border-slate-700 transition-all w-full sm:w-auto">
                            Learn Methodology
                        </button>
                    </div>

                    <div className="mt-12 grid grid-cols-3 gap-6 border-t border-slate-800 pt-8">
                        <div>
                            <h3 className="text-3xl font-bold text-white">96%</h3>
                            <p className="text-sm text-slate-400">Accuracy</p>
                        </div>
                        <div>
                            <h3 className="text-3xl font-bold text-white">&lt;2s</h3>
                            <p className="text-sm text-slate-400">Inference Time</p>
                        </div>
                        <div>
                            <h3 className="text-3xl font-bold text-white">24/7</h3>
                            <p className="text-sm text-slate-400">Availability</p>
                        </div>
                    </div>
                </motion.div>

                {/* Right Visual */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="relative"
                >
                    <div className="relative z-10 bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-2xl p-6 shadow-2xl">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                            </div>
                            <div className="text-xs text-slate-500 font-mono">Analysis_v1.0.py</div>
                        </div>
                        <div className="space-y-4">
                            {/* Simulation of scanning */}
                            <div className="h-48 rounded-xl bg-black/50 border border-slate-700 relative overflow-hidden flex items-center justify-center group">
                                <Brain className="w-24 h-24 text-slate-600 group-hover:text-primary transition-colors duration-500" />
                                <div className="absolute top-0 left-0 w-full h-1 bg-primary/50 shadow-[0_0_15px_rgba(99,102,241,0.8)] animate-[scan_2s_ease-in-out_infinite]"></div>
                            </div>
                            <div className="flex gap-4">
                                <div className="flex-1 p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                                    <div className="text-xs text-slate-400 mb-1">Status</div>
                                    <div className="text-green-400 font-mono text-sm flex items-center gap-2">
                                        <ShieldCheck className="w-4 h-4" /> Normal
                                    </div>
                                </div>
                                <div className="flex-1 p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                                    <div className="text-xs text-slate-400 mb-1">Confidence</div>
                                    <div className="text-white font-mono text-sm">98.42%</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Floating Elements */}
                    <motion.div
                        animate={{ y: [0, -20, 0] }}
                        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                        className="absolute -top-6 -right-6 p-4 bg-secondary/10 backdrop-blur-md border border-secondary/20 rounded-xl"
                    >
                        <Activity className="w-8 h-8 text-secondary" />
                    </motion.div>
                </motion.div>
            </div>
        </div>
    );
};

export default Landing;
