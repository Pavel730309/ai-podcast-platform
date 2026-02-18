import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import {
  Play, Pause, Download, Clock, CheckCircle, AlertCircle,
  Loader, Volume2, VolumeX, SkipBack, SkipForward,
  RefreshCw, ArrowLeft, Rss, Share2, Music, Archive, FileAudio, Image
} from 'lucide-react';
import toast from 'react-hot-toast';
import { podcastApi } from '../services/podcastApi';
import { exportApi } from '../services/exportApi';
import type { Podcast, ProgressResponse } from '../types/api';

// ─── Audio Player Component ───────────────────────────────────────────────────
const AudioPlayer = ({ audioUrl, title }: { audioUrl: string; title: string }) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const formatTime = (seconds: number) => {
    if (isNaN(seconds)) return '0:00';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play().catch(() => toast.error('Не удалось воспроизвести аудио'));
    }
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!audioRef.current || !progressRef.current) return;
    const rect = progressRef.current.getBoundingClientRect();
    const ratio = (e.clientX - rect.left) / rect.width;
    audioRef.current.currentTime = ratio * duration;
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setVolume(val);
    if (audioRef.current) audioRef.current.volume = val;
    setIsMuted(val === 0);
  };

  const toggleMute = () => {
    if (!audioRef.current) return;
    const newMuted = !isMuted;
    setIsMuted(newMuted);
    audioRef.current.muted = newMuted;
  };

  const skip = (seconds: number) => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = Math.max(0, Math.min(duration, currentTime + seconds));
  };

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-xl p-6 text-white">
      <div className="flex items-center mb-4">
        <Music className="h-5 w-5 mr-2 opacity-80" />
        <span className="text-sm font-medium opacity-80 truncate">{title}</span>
      </div>

      <audio
        ref={audioRef}
        src={audioUrl}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onTimeUpdate={() => setCurrentTime(audioRef.current?.currentTime || 0)}
        onLoadedMetadata={() => {
          setDuration(audioRef.current?.duration || 0);
          setIsLoading(false);
        }}
        onWaiting={() => setIsLoading(true)}
        onCanPlay={() => setIsLoading(false)}
        onEnded={() => setIsPlaying(false)}
      />

      {/* Progress bar */}
      <div
        ref={progressRef}
        className="w-full bg-white/20 rounded-full h-2 mb-4 cursor-pointer group"
        onClick={handleProgressClick}
      >
        <div
          className="bg-white h-2 rounded-full transition-all relative"
          style={{ width: `${progressPercent}%` }}
        >
          <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </div>

      {/* Time */}
      <div className="flex justify-between text-xs opacity-70 mb-4">
        <span>{formatTime(currentTime)}</span>
        <span>{formatTime(duration)}</span>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleMute}
            className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
          >
            {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={isMuted ? 0 : volume}
            onChange={handleVolumeChange}
            className="w-20 accent-white"
          />
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => skip(-10)}
            className="p-2 hover:bg-white/20 rounded-full transition-colors"
            title="-10 сек"
          >
            <SkipBack className="h-5 w-5" />
          </button>

          <button
            onClick={togglePlay}
            disabled={isLoading}
            className="bg-white text-primary-700 rounded-full p-3 hover:bg-primary-50 transition-colors disabled:opacity-50"
          >
            {isLoading ? (
              <Loader className="h-6 w-6 animate-spin" />
            ) : isPlaying ? (
              <Pause className="h-6 w-6" />
            ) : (
              <Play className="h-6 w-6 ml-0.5" />
            )}
          </button>

          <button
            onClick={() => skip(10)}
            className="p-2 hover:bg-white/20 rounded-full transition-colors"
            title="+10 сек"
          >
            <SkipForward className="h-5 w-5" />
          </button>
        </div>

        <a
          href={audioUrl}
          download
          className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
          title="Скачать"
        >
          <Download className="h-4 w-4" />
        </a>
      </div>
    </div>
  );
};

// ─── Progress Steps ───────────────────────────────────────────────────────────
const STEPS = [
  { key: 'extracting_text', label: 'Извлечение текста', percent: 10 },
  { key: 'generating_scenario', label: 'Генерация сценария', percent: 30 },
  { key: 'synthesizing_speech', label: 'Синтез речи', percent: 50 },
  { key: 'processing_audio', label: 'Обработка аудио', percent: 70 },
  { key: 'generating_cover', label: 'Генерация обложки', percent: 90 },
  { key: 'completed', label: 'Готово', percent: 100 },
];

const ProcessingProgress = ({ status, progress }: { status: string; progress: ProgressResponse | null }) => {
  const currentPercent = progress?.progress_percent || 0;
  const currentStep = progress?.current_step || 'Обработка...';

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Loader className="h-5 w-5 mr-2 text-primary-600 animate-spin" />
        Создание подкаста
      </h2>

      {/* Main progress bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-600">{currentStep}</span>
          <span className="font-medium text-primary-600">{currentPercent}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-primary-600 h-3 rounded-full transition-all duration-700 ease-out"
            style={{ width: `${currentPercent}%` }}
          />
        </div>
      </div>

      {/* Step indicators */}
      <div className="flex justify-between mt-4">
        {STEPS.map((step, i) => {
          const isDone = currentPercent >= step.percent;
          const isCurrent = status === step.key;
          return (
            <div key={step.key} className="flex flex-col items-center flex-1">
              <div
                className={`w-3 h-3 rounded-full mb-1 transition-colors ${
                  isDone
                    ? 'bg-primary-600'
                    : isCurrent
                    ? 'bg-primary-400 animate-pulse'
                    : 'bg-gray-300'
                }`}
              />
              <span className={`text-xs text-center hidden md:block ${isDone ? 'text-primary-600' : 'text-gray-400'}`}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ─── Main Page ────────────────────────────────────────────────────────────────
const PodcastDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [podcast, setPodcast] = useState<Podcast | null>(null);
  const [progress, setProgress] = useState<ProgressResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRetrying, setIsRetrying] = useState(false);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const isProcessing = useCallback((status: string) => {
    return !['completed', 'failed'].includes(status);
  }, []);

  const fetchPodcast = useCallback(async () => {
    if (!id) return;
    try {
      const data = await podcastApi.getPodcast(id);
      setPodcast(data);
      return data;
    } catch {
      toast.error('Не удалось загрузить подкаст');
      return null;
    }
  }, [id]);

  const fetchProgress = useCallback(async () => {
    if (!id) return;
    try {
      const data = await podcastApi.getProgress(id);
      setProgress(data);

      // Update podcast status from progress
      setPodcast((prev) => {
        if (!prev) return prev;
        return { ...prev, status: data.status };
      });

      // Stop polling if done
      if (!isProcessing(data.status)) {
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
        // Refresh full podcast data when completed
        if (data.status === 'completed') {
          fetchPodcast();
        }
      }
    } catch (err) {
      console.error('Progress fetch error:', err);
    }
  }, [id, isProcessing, fetchPodcast]);

  useEffect(() => {
    const init = async () => {
      setIsLoading(true);
      const data = await fetchPodcast();
      setIsLoading(false);

      if (data && isProcessing(data.status)) {
        // Start polling
        await fetchProgress();
        pollingRef.current = setInterval(fetchProgress, 3000);
      }
    };
    init();

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [id]);

  const handleRetry = async () => {
    if (!id) return;
    setIsRetrying(true);
    try {
      await podcastApi.retryPodcast(id);
      toast.success('Повторная генерация запущена');
      const data = await fetchPodcast();
      if (data && isProcessing(data.status)) {
        pollingRef.current = setInterval(fetchProgress, 3000);
      }
    } catch {
      toast.error('Не удалось запустить повторную генерацию');
    } finally {
      setIsRetrying(false);
    }
  };

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    toast.success('Ссылка скопирована');
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed': return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'pending': return <Clock className="h-5 w-5 text-gray-400" />;
      default: return <Loader className="h-5 w-5 text-primary-500 animate-spin" />;
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      completed: 'Готов',
      failed: 'Ошибка',
      pending: 'Ожидание',
      extracting_text: 'Извлечение текста',
      generating_scenario: 'Генерация сценария',
      synthesizing_speech: 'Синтез речи',
      processing_audio: 'Обработка аудио',
      generating_cover: 'Генерация обложки',
    };
    return labels[status] || status;
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (!podcast) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-gray-300 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Подкаст не найден</h2>
        <Link to="/" className="text-primary-600 hover:text-primary-700">
          ← Вернуться к списку
        </Link>
      </div>
    );
  }

  const processing = isProcessing(podcast.status);

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back button */}
      <Link
        to="/"
        className="inline-flex items-center text-gray-500 hover:text-gray-700 mb-6 transition-colors"
      >
        <ArrowLeft className="h-4 w-4 mr-1" />
        Назад к списку
      </Link>

      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">{podcast.title}</h1>
            {podcast.description && (
              <p className="text-gray-600 mb-3">{podcast.description}</p>
            )}
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span className="flex items-center gap-1">
                {getStatusIcon(podcast.status)}
                {getStatusLabel(podcast.status)}
              </span>
              {podcast.duration_seconds && (
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {Math.floor(podcast.duration_seconds / 60)}:{(podcast.duration_seconds % 60).toString().padStart(2, '0')}
                </span>
              )}
              <span>{new Date(podcast.created_at).toLocaleDateString('ru-RU')}</span>
            </div>
          </div>

          {/* Cover image */}
          {podcast.cover_image && (
            <img
              src={podcast.cover_image}
              alt={podcast.title}
              className="w-24 h-24 object-cover rounded-lg shadow-md ml-4 flex-shrink-0"
            />
          )}
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-3 mt-4 pt-4 border-t border-gray-100">
          <button
            onClick={handleShare}
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-800 px-3 py-1.5 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <Share2 className="h-4 w-4 mr-1.5" />
            Поделиться
          </button>
          {podcast.rss_feed && (
            <a
              href={podcast.rss_feed}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-sm text-orange-600 hover:text-orange-700 px-3 py-1.5 rounded-lg hover:bg-orange-50 transition-colors"
            >
              <Rss className="h-4 w-4 mr-1.5" />
              RSS Feed
            </a>
          )}
          {podcast.status === 'failed' && (
            <button
              onClick={handleRetry}
              disabled={isRetrying}
              className="inline-flex items-center text-sm text-primary-600 hover:text-primary-700 px-3 py-1.5 rounded-lg hover:bg-primary-50 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 mr-1.5 ${isRetrying ? 'animate-spin' : ''}`} />
              Повторить генерацию
            </button>
          )}
        </div>
      </div>

      {/* Processing progress */}
      {processing && (
        <ProcessingProgress status={podcast.status} progress={progress} />
      )}

      {/* Error message */}
      {podcast.status === 'failed' && podcast.error_message && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-5 mb-6">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-red-500 mr-3 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="text-red-800 font-medium mb-1">Ошибка генерации</h3>
              <p className="text-red-700 text-sm">{podcast.error_message}</p>
            </div>
          </div>
        </div>
      )}

      {/* Audio Player */}
      {podcast.status === 'completed' && podcast.audio_file && (
        <div className="mb-6">
          <AudioPlayer audioUrl={podcast.audio_file} title={podcast.title} />
        </div>
      )}

      {/* Cover Image (large) */}
      {podcast.status === 'completed' && podcast.cover_image && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Обложка подкаста</h2>
          <div className="flex items-start gap-6">
            <img
              src={podcast.cover_image}
              alt={podcast.title}
              className="w-48 h-48 object-cover rounded-xl shadow-md"
            />
            <div className="flex-1">
              <p className="text-gray-600 text-sm mb-4">
                Обложка создана автоматически с помощью AI на основе темы вашего подкаста.
              </p>
              <a
                href={podcast.cover_image}
                download
                className="inline-flex items-center text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                <Download className="h-4 w-4 mr-1.5" />
                Скачать обложку
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Export section */}
      {podcast.status === 'completed' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Экспорт и скачивание</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {podcast.audio_file && (
              <button
                onClick={() => {
                  exportApi.downloadAudio(podcast.id);
                  toast.success('Скачивание аудио начато');
                }}
                className="flex items-center justify-center gap-2 px-4 py-3 bg-primary-50 hover:bg-primary-100 text-primary-700 rounded-xl border border-primary-200 transition-colors font-medium text-sm"
              >
                <FileAudio className="h-5 w-5" />
                Скачать MP3
              </button>
            )}
            {podcast.cover_image && (
              <button
                onClick={() => {
                  exportApi.downloadCover(podcast.id);
                  toast.success('Скачивание обложки начато');
                }}
                className="flex items-center justify-center gap-2 px-4 py-3 bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-xl border border-purple-200 transition-colors font-medium text-sm"
              >
                <Image className="h-5 w-5" />
                Скачать обложку
              </button>
            )}
            <button
              onClick={() => {
                exportApi.downloadZip(podcast.id);
                toast.success('Подготовка архива...');
              }}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-xl border border-gray-200 transition-colors font-medium text-sm"
            >
              <Archive className="h-5 w-5" />
              Скачать ZIP
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-3">
            ZIP-архив содержит аудио, обложку, RSS-фид и метаданные подкаста
          </p>
        </div>
      )}

      {/* Details */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Детали подкаста</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500 mb-1">Стиль</p>
            <p className="font-medium text-gray-900 capitalize">
              {podcast.style === 'academic' ? '🎓 Академический' :
               podcast.style === 'entertainment' ? '🎭 Развлекательный' :
               podcast.style === 'business' ? '💼 Бизнес' : podcast.style}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500 mb-1">Участников</p>
            <p className="font-medium text-gray-900">{podcast.num_participants}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500 mb-1">Источник</p>
            <p className="font-medium text-gray-900 uppercase">{podcast.source_type}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500 mb-1">Создан</p>
            <p className="font-medium text-gray-900">
              {new Date(podcast.created_at).toLocaleDateString('ru-RU')}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PodcastDetailPage;
