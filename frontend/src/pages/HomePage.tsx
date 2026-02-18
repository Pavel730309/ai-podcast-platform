import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Mic, FileText, Play, Zap, Clock, CheckCircle, AlertCircle, Loader, Plus, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { podcastApi } from '../services/podcastApi';
import type { Podcast } from '../types/api';

const StatusBadge = ({ status }: { status: string }) => {
  const config: Record<string, { label: string; className: string; icon: React.ReactNode }> = {
    completed: {
      label: 'Готов',
      className: 'bg-green-100 text-green-800',
      icon: <CheckCircle className="h-3 w-3 mr-1" />,
    },
    failed: {
      label: 'Ошибка',
      className: 'bg-red-100 text-red-800',
      icon: <AlertCircle className="h-3 w-3 mr-1" />,
    },
    pending: {
      label: 'Ожидание',
      className: 'bg-gray-100 text-gray-700',
      icon: <Clock className="h-3 w-3 mr-1" />,
    },
  };

  const isProcessing = !['completed', 'failed', 'pending'].includes(status);
  const cfg = config[status] || {
    label: status.replace(/_/g, ' '),
    className: 'bg-blue-100 text-blue-800',
    icon: <Loader className="h-3 w-3 mr-1 animate-spin" />,
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${cfg.className}`}>
      {cfg.icon}
      {cfg.label}
    </span>
  );
};

const PodcastCard = ({
  podcast,
  onDelete,
}: {
  podcast: Podcast;
  onDelete: (id: string) => void;
}) => {
  const formatDuration = (seconds?: number) => {
    if (!seconds) return null;
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const styleLabels: Record<string, string> = {
    academic: '🎓 Академический',
    entertainment: '🎭 Развлекательный',
    business: '💼 Бизнес',
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <Link
            to={`/podcast/${podcast.id}`}
            className="text-lg font-semibold text-gray-900 hover:text-primary-600 transition-colors line-clamp-1"
          >
            {podcast.title}
          </Link>
          {podcast.description && (
            <p className="text-sm text-gray-500 mt-1 line-clamp-2">{podcast.description}</p>
          )}
        </div>
        <button
          onClick={() => onDelete(podcast.id)}
          className="ml-3 p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors flex-shrink-0"
          title="Удалить подкаст"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        <StatusBadge status={podcast.status} />
        <span className="text-xs text-gray-500">
          {styleLabels[podcast.style] || podcast.style}
        </span>
        {podcast.duration_seconds && (
          <span className="text-xs text-gray-500 flex items-center">
            <Clock className="h-3 w-3 mr-1" />
            {formatDuration(podcast.duration_seconds)}
          </span>
        )}
        <span className="text-xs text-gray-400 ml-auto">
          {new Date(podcast.created_at).toLocaleDateString('ru-RU')}
        </span>
      </div>

      {podcast.status === 'completed' && podcast.audio_file && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <Link
            to={`/podcast/${podcast.id}`}
            className="inline-flex items-center text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            <Play className="h-4 w-4 mr-1" />
            Слушать подкаст
          </Link>
        </div>
      )}
    </div>
  );
};

const HomePage = () => {
  const [podcasts, setPodcasts] = useState<Podcast[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showLanding, setShowLanding] = useState(false);

  useEffect(() => {
    fetchPodcasts();
  }, []);

  const fetchPodcasts = async () => {
    try {
      setIsLoading(true);
      const data = await podcastApi.getPodcasts(0, 20);
      setPodcasts(data);
      setShowLanding(data.length === 0);
    } catch (error) {
      console.error('Failed to load podcasts:', error);
      setShowLanding(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Удалить этот подкаст?')) return;
    try {
      await podcastApi.deletePodcast(id);
      setPodcasts((prev) => prev.filter((p) => p.id !== id));
      toast.success('Подкаст удалён');
    } catch {
      toast.error('Не удалось удалить подкаст');
    }
  };

  // Landing page for new users
  if (showLanding && !isLoading) {
    return (
      <div className="max-w-7xl mx-auto">
        {/* Hero */}
        <section className="py-16 md:py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Создавайте AI-подкасты
              <span className="text-primary-600"> из текста</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-10">
              Загрузите документ, вставьте текст или укажите URL — и получите профессиональный подкаст с несколькими голосами, фоновой музыкой и обложкой.
            </p>
            <Link
              to="/create"
              className="inline-flex items-center bg-primary-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-primary-700 transition-colors shadow-lg text-lg"
            >
              <Plus className="h-5 w-5 mr-2" />
              Создать первый подкаст
            </Link>
          </div>
        </section>

        {/* Features */}
        <section className="py-12 bg-white rounded-2xl shadow-sm mb-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 px-8">
            <div className="text-center p-6">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Любые источники</h3>
              <p className="text-gray-600">PDF, DOCX, текст или URL — система извлечёт контент автоматически.</p>
            </div>
            <div className="text-center p-6">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Mic className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">AI-диалоги</h3>
              <p className="text-gray-600">Несколько ведущих с разными голосами, естественные переходы между темами.</p>
            </div>
            <div className="text-center p-6">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Полная автоматизация</h3>
              <p className="text-gray-600">Музыка, обложка, RSS-фид — всё создаётся автоматически.</p>
            </div>
          </div>
        </section>

        {/* How it works */}
        <section className="py-12">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-10">Как это работает</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { step: 1, title: 'Загрузите контент', desc: 'PDF, DOCX, текст или ссылку на статью' },
              { step: 2, title: 'AI создаёт сценарий', desc: 'Диалог с несколькими ведущими' },
              { step: 3, title: 'Синтез речи', desc: 'Профессиональные голоса + фоновая музыка' },
              { step: 4, title: 'Скачайте и поделитесь', desc: 'MP3 файл + RSS для платформ' },
            ].map(({ step, title, desc }) => (
              <div key={step} className="text-center">
                <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-lg">
                  {step}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
                <p className="text-gray-600 text-sm">{desc}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    );
  }

  // Podcasts list
  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Мои подкасты</h1>
          <p className="text-gray-500 mt-1">
            {isLoading ? 'Загрузка...' : `${podcasts.length} подкаст${podcasts.length === 1 ? '' : podcasts.length < 5 ? 'а' : 'ов'}`}
          </p>
        </div>
        <Link
          to="/create"
          className="inline-flex items-center bg-primary-600 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-4 w-4 mr-2" />
          Создать подкаст
        </Link>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-48">
          <Loader className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      ) : podcasts.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
          <Mic className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Нет подкастов</h3>
          <p className="text-gray-500 mb-6">Создайте свой первый AI-подкаст</p>
          <Link
            to="/create"
            className="inline-flex items-center bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors"
          >
            <Plus className="h-4 w-4 mr-2" />
            Создать подкаст
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {podcasts.map((podcast) => (
            <PodcastCard key={podcast.id} podcast={podcast} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  );
};

export default HomePage;
