import React from 'react';
import { Link } from 'react-router-dom';
import { Mic, FileText, Play, Zap, Users, Clock, Star } from 'lucide-react';

const HomePage = () => {
  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <section className="py-16 md:py-24">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Create AI-Powered
            <span className="text-primary-600"> Podcasts</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-10">
            Transform your text into engaging podcasts with AI. Upload documents, paste text, or enter a URL and let our platform create professional-quality audio content.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              to="/create" 
              className="bg-primary-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-primary-700 transition-colors shadow-lg"
            >
              Create Your First Podcast
            </Link>
            <Link 
              to="/podcasts" 
              className="border border-primary-600 text-primary-600 px-8 py-4 rounded-lg font-semibold hover:bg-primary-50 transition-colors"
            >
              View My Podcasts
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white rounded-2xl shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center p-6">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Multiple Sources</h3>
            <p className="text-gray-600">
              Upload PDFs, DOCX files, or paste text from any website. Our system extracts and processes content seamlessly.
            </p>
          </div>
          
          <div className="text-center p-6">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mic className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">AI-Powered Dialogues</h3>
            <p className="text-gray-600">
              Our AI creates natural-sounding dialogues with multiple participants, perfect for educational, business, or entertainment podcasts.
            </p>
          </div>
          
          <div className="text-center p-6">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Play className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Professional Audio</h3>
            <p className="text-gray-600">
              Generate high-quality audio with natural-sounding voices, background music, and professional sound mixing.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-lg">
              1
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Content</h3>
            <p className="text-gray-600">
              Upload documents, paste text, or enter a URL to get started.
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-lg">
              2
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Processing</h3>
            <p className="text-gray-600">
              Our AI transforms your text into engaging podcast dialogues.
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-lg">
              3
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Customize</h3>
            <p className="text-gray-600">
              Choose voices, styles, and add background music to personalize your podcast.
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-lg">
              4
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Download & Share</h3>
            <p className="text-gray-600">
              Download your finished podcast or publish directly to podcast platforms.
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-2xl text-white">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold mb-2">10K+</div>
            <div className="text-primary-100">Podcasts Created</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">50+</div>
            <div className="text-primary-100">Voices Available</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">99%</div>
            <div className="text-primary-100">Accuracy Rate</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">24/7</div>
            <div className="text-primary-100">Support</div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;