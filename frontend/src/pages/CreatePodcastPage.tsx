import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Upload, FileText, Globe, Mic, Settings, Play, Clock, Zap } from 'lucide-react';
import toast from 'react-hot-toast';
import { podcastApi } from '../services/podcastApi';
import { textExtractionApi } from '../services/textExtractionApi';
import type { PodcastCreate, Podcast } from '../types/api';

const CreatePodcastPage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'file' | 'url' | 'text'>('file');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [urlInput, setUrlInput] = useState('');
  const [textInput, setTextInput] = useState('');
  const [extractedText, setExtractedText] = useState('');
  const [podcastTitle, setPodcastTitle] = useState('');
  const [podcastStyle, setPodcastStyle] = useState<'academic' | 'entertainment' | 'business'>('entertainment');
  const [numParticipants, setNumParticipants] = useState(2);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const extractContent = async () => {
    setIsExtracting(true);
    try {
      let result;
      if (activeTab === 'file' && selectedFile) {
        result = await textExtractionApi.extractFromFile(selectedFile);
      } else if (activeTab === 'url' && urlInput) {
        result = await textExtractionApi.extractFromUrl(urlInput);
      } else if (activeTab === 'text' && textInput) {
        result = await textExtractionApi.extractFromText(textInput);
      } else {
        toast.error('Please provide content');
        return null;
      }
      
      if (result.error) {
        toast.error(result.error);
        return null;
      }
      
      setExtractedText(result.text);
      return result.text;
    } catch (error) {
      toast.error('Failed to extract content');
      return null;
    } finally {
      setIsExtracting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!podcastTitle) {
      toast.error('Please enter a podcast title');
      return;
    }

    setIsGenerating(true);
    
    try {
      // Step 1: Extract content if needed
      let sourceText = extractedText;
      if (!sourceText) {
        sourceText = await extractContent() || '';
      }
      
      if (!sourceText) {
        setIsGenerating(false);
        return;
      }

      // Step 2: Create podcast
      const podcastData: PodcastCreate = {
        title: podcastTitle,
        style: podcastStyle,
        num_participants: numParticipants,
        source_type: activeTab,
        source_text: sourceText,
        source_url: activeTab === 'url' ? urlInput : undefined,
        participants: Array.from({ length: numParticipants }, (_, i) => ({
          name: i === 0 ? 'Host' : `Guest ${i}`,
          role: i === 0 ? 'host' : 'expert',
          voice_provider: 'openai',
          voice_id: i === 0 ? 'alloy' : i === 1 ? 'echo' : 'fable',
        })),
      };

      const podcast: Podcast = await podcastApi.createPodcast(podcastData);
      
      toast.success('Podcast created successfully!');
      navigate(`/podcast/${podcast.id}`);
    } catch (error) {
      toast.error('Failed to create podcast');
      console.error(error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Create New Podcast</h1>
        <p className="text-gray-600">Transform your content into an engaging podcast</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {/* Step 1: Source Selection */}
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <span className="bg-primary-100 text-primary-800 rounded-full w-6 h-6 flex items-center justify-center mr-2">1</span>
            Select Content Source
          </h2>
          
          <div className="flex space-x-4 mb-6">
            <button
              type="button"
              onClick={() => setActiveTab('file')}
              className={`flex items-center px-4 py-2 rounded-lg border ${
                activeTab === 'file'
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Upload className="h-5 w-5 mr-2" />
              Upload File
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('url')}
              className={`flex items-center px-4 py-2 rounded-lg border ${
                activeTab === 'url'
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Globe className="h-5 w-5 mr-2" />
              From URL
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('text')}
              className={`flex items-center px-4 py-2 rounded-lg border ${
                activeTab === 'text'
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <FileText className="h-5 w-5 mr-2" />
              Paste Text
            </button>
          </div>

          {/* File Upload */}
          {activeTab === 'file' && (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">
                {selectedFile ? selectedFile.name : 'Drag and drop your file here'}
              </p>
              <p className="text-sm text-gray-500 mb-4">Supported formats: PDF, DOCX</p>
              <label className="inline-block bg-primary-600 text-white px-4 py-2 rounded-lg cursor-pointer hover:bg-primary-700 transition-colors">
                Browse Files
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                />
              </label>
            </div>
          )}

          {/* URL Input */}
          {activeTab === 'url' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Website URL
                </label>
                <input
                  type="url"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://example.com/article"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
          )}

          {/* Text Input */}
          {activeTab === 'text' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Paste your text here
                </label>
                <textarea
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  rows={6}
                  placeholder="Enter or paste your content here..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
          )}

          {/* Extracted Text Preview */}
          {extractedText && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium text-gray-700 mb-2">Extracted Text Preview:</p>
              <p className="text-sm text-gray-600 line-clamp-3">{extractedText}</p>
            </div>
          )}
        </div>

        {/* Step 2: Podcast Settings */}
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <span className="bg-primary-100 text-primary-800 rounded-full w-6 h-6 flex items-center justify-center mr-2">2</span>
            Podcast Settings
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Podcast Title
              </label>
              <input
                type="text"
                value={podcastTitle}
                onChange={(e) => setPodcastTitle(e.target.value)}
                placeholder="Enter podcast title"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Podcast Style
              </label>
              <select
                value={podcastStyle}
                onChange={(e) => setPodcastStyle(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="entertainment">Entertainment</option>
                <option value="academic">Academic</option>
                <option value="business">Business</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Number of Participants
              </label>
              <div className="flex items-center space-x-4">
                <button
                  type="button"
                  onClick={() => setNumParticipants(Math.max(2, numParticipants - 1))}
                  className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-50"
                >
                  -
                </button>
                <span className="text-lg font-medium">{numParticipants}</span>
                <button
                  type="button"
                  onClick={() => setNumParticipants(Math.min(4, numParticipants + 1))}
                  className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-50"
                >
                  +
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Step 3: Preview and Generate */}
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <span className="bg-primary-100 text-primary-800 rounded-full w-6 h-6 flex items-center justify-center mr-2">3</span>
            Review & Generate
          </h2>
          
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="flex items-start mb-4">
              <div className="bg-primary-100 p-2 rounded-lg mr-3">
                <Settings className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Your Podcast Configuration</h3>
                <ul className="mt-2 text-sm text-gray-600 space-y-1">
                  <li className="flex items-center">
                    <Clock className="h-4 w-4 mr-2 text-gray-400" />
                    <span>Source: {activeTab === 'file' ? 'File' : activeTab === 'url' ? 'URL' : 'Text'}</span>
                  </li>
                  <li className="flex items-center">
                    <Mic className="h-4 w-4 mr-2 text-gray-400" />
                    <span>{numParticipants} participants</span>
                  </li>
                  <li className="flex items-center">
                    <Zap className="h-4 w-4 mr-2 text-gray-400" />
                    <span>Style: {podcastStyle.charAt(0).toUpperCase() + podcastStyle.slice(1)}</span>
                  </li>
                </ul>
              </div>
            </div>
            
            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <div className="text-sm text-gray-500">
                {activeTab === 'file' && selectedFile && (
                  <span>File: {selectedFile.name}</span>
                )}
                {activeTab === 'url' && urlInput && (
                  <span>URL: {urlInput.substring(0, 50)}...</span>
                )}
                {activeTab === 'text' && textInput && (
                  <span>Text: {textInput.length} characters</span>
                )}
              </div>
              
              <button
                type="submit"
                disabled={isGenerating || isExtracting || !podcastTitle}
                className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {isGenerating || isExtracting ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {isExtracting ? 'Extracting...' : 'Creating...'}
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5 mr-2" />
                    Generate Podcast
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </form>
      
      <div className="mt-8 text-center">
        <Link 
          to="/podcasts" 
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          ← Back to My Podcasts
        </Link>
      </div>
    </div>
  );
};

export default CreatePodcastPage;
