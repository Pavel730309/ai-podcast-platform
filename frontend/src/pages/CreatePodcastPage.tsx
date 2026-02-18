import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Upload, FileText, Globe, Mic, Settings, Play,
  Clock, Zap, ChevronRight, ChevronLeft, User, Music2
} from 'lucide-react';
import toast from 'react-hot-toast';
import { podcastApi } from '../services/podcastApi';
import { textExtractionApi } from '../services/textExtractionApi';
import type { PodcastCreate, Podcast } from '../types/api';

// ─── Voice options ────────────────────────────────────────────────────────────
const OPENAI_VOICES = [
  { id: 'alloy', name: 'Alloy', gender: 'neutral', desc: 'Нейтральный, сбалансированный' },
  { id: 'echo', name: 'Echo', gender: 'male', desc: 'Мужской, чёткий' },
  { id: 'fable', name: 'Fable', gender: 'male', desc: 'Мужской, выразительный' },
  { id: 'onyx', name: 'Onyx', gender: 'male', desc: 'Мужской, глубокий' },
  { id: 'nova', name: 'Nova', gender: 'female', desc: 'Женский, живой' },
  { id: 'shimmer', name: 'Shimmer', gender: 'female', desc: 'Женский, мягкий' },
];

const ROLES = [
  { id: 'host', label: 'Ведущий', desc: 'Задаёт вопросы, ведёт беседу' },
  { id: 'expert', label: 'Эксперт', desc: 'Даёт развёрнутые ответы' },
  { id: 'commentator', label: 'Комментатор', desc: 'Добавляет мнения и оценки' },
];

const DEFAULT_NAMES = ['Алекс', 'Джордан', 'Сэм', 'Тейлор'];
const DEFAULT_VOICES = ['alloy', 'echo', 'fable', 'nova'];

interface ParticipantConfig {
  name: string;
  role: string;
  voice_provider: string;
  voice_id: string;
}

// ─── Step indicator ───────────────────────────────────────────────────────────
const StepIndicator = ({ current, total }: { current: number; total: number }) => (
  <div className="flex items-center justify-center mb-8">
    {Array.from({ length: total }, (_, i) => (
      <React.Fragment key={i}>
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
            i + 1 === current
              ? 'bg-primary-600 text-white'
              : i + 1 < current
              ? 'bg-primary-200 text-primary-700'
              : 'bg-gray-200 text-gray-500'
          }`}
        >
          {i + 1}
        </div>
        {i < total - 1 && (
          <div className={`h-0.5 w-12 mx-1 ${i + 1 < current ? 'bg-primary-300' : 'bg-gray-200'}`} />
        )}
      </React.Fragment>
    ))}
  </div>
);

// ─── Main Component ───────────────────────────────────────────────────────────
const CreatePodcastPage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);

  // Step 1: Source
  const [activeTab, setActiveTab] = useState<'file' | 'url' | 'text'>('text');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [urlInput, setUrlInput] = useState('');
  const [textInput, setTextInput] = useState('');
  const [extractedText, setExtractedText] = useState('');
  const [isExtracting, setIsExtracting] = useState(false);

  // Step 2: Settings
  const [podcastTitle, setPodcastTitle] = useState('');
  const [podcastDescription, setPodcastDescription] = useState('');
  const [podcastStyle, setPodcastStyle] = useState<'academic' | 'entertainment' | 'business'>('entertainment');
  const [numParticipants, setNumParticipants] = useState(2);

  // Step 3: Voices
  const [participants, setParticipants] = useState<ParticipantConfig[]>([
    { name: 'Алекс', role: 'host', voice_provider: 'openai', voice_id: 'alloy' },
    { name: 'Джордан', role: 'expert', voice_provider: 'openai', voice_id: 'echo' },
  ]);

  // Step 4: Generate
  const [isGenerating, setIsGenerating] = useState(false);

  // ─── Handlers ───────────────────────────────────────────────────────────────

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setSelectedFile(e.target.files[0]);
  };

  const handleExtract = async () => {
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
        toast.error('Укажите источник контента');
        return false;
      }

      if (result.error) {
        toast.error(result.error);
        return false;
      }

      setExtractedText(result.text);
      if (result.title && !podcastTitle) setPodcastTitle(result.title);
      toast.success(`Извлечено ${result.word_count} слов`);
      return true;
    } catch {
      toast.error('Не удалось извлечь контент');
      return false;
    } finally {
      setIsExtracting(false);
    }
  };

  const handleStep1Next = async () => {
    // For text tab, use directly without extraction
    if (activeTab === 'text' && textInput && !extractedText) {
      setExtractedText(textInput);
      setStep(2);
      return;
    }
    if (extractedText) {
      setStep(2);
      return;
    }
    const ok = await handleExtract();
    if (ok) setStep(2);
  };

  const handleStep2Next = () => {
    if (!podcastTitle.trim()) {
      toast.error('Введите название подкаста');
      return;
    }
    // Sync participants count
    const newParticipants = Array.from({ length: numParticipants }, (_, i) => ({
      name: participants[i]?.name || DEFAULT_NAMES[i],
      role: participants[i]?.role || (i === 0 ? 'host' : 'expert'),
      voice_provider: participants[i]?.voice_provider || 'openai',
      voice_id: participants[i]?.voice_id || DEFAULT_VOICES[i],
    }));
    setParticipants(newParticipants);
    setStep(3);
  };

  const updateParticipant = (index: number, field: keyof ParticipantConfig, value: string) => {
    setParticipants((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };

  const handleSubmit = async () => {
    setIsGenerating(true);
    try {
      const podcastData: PodcastCreate = {
        title: podcastTitle,
        description: podcastDescription || undefined,
        style: podcastStyle,
        num_participants: numParticipants,
        source_type: activeTab === 'file' ? 'pdf' : activeTab,
        source_text: extractedText,
        source_url: activeTab === 'url' ? urlInput : undefined,
        participants: participants.map((p) => ({
          name: p.name,
          role: p.role,
          voice_provider: p.voice_provider,
          voice_id: p.voice_id,
        })),
      };

      const podcast: Podcast = await podcastApi.createPodcast(podcastData);
      toast.success('Подкаст создан! Начинается генерация...');
      navigate(`/podcast/${podcast.id}`);
    } catch (error: any) {
      const msg = error?.response?.data?.detail || 'Не удалось создать подкаст';
      toast.error(msg);
    } finally {
      setIsGenerating(false);
    }
  };

  // ─── Render steps ────────────────────────────────────────────────────────────

  const renderStep1 = () => (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Выберите источник контента</h2>

      {/* Tabs */}
      <div className="flex space-x-2 mb-6">
        {[
          { id: 'text', label: 'Текст', icon: <FileText className="h-4 w-4" /> },
          { id: 'url', label: 'URL', icon: <Globe className="h-4 w-4" /> },
          { id: 'file', label: 'Файл', icon: <Upload className="h-4 w-4" /> },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'border-primary-500 bg-primary-50 text-primary-700'
                : 'border-gray-300 text-gray-600 hover:bg-gray-50'
            }`}
          >
            {tab.icon}
            <span className="ml-2">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Text input */}
      {activeTab === 'text' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Вставьте текст для подкаста
          </label>
          <textarea
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            rows={10}
            placeholder="Вставьте статью, эссе, доклад или любой другой текст (минимум 200 символов)..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
          />
          <p className="text-xs text-gray-400 mt-1">{textInput.length} символов</p>
        </div>
      )}

      {/* URL input */}
      {activeTab === 'url' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            URL статьи или страницы
          </label>
          <input
            type="url"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="https://example.com/article"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          {urlInput && (
            <button
              type="button"
              onClick={handleExtract}
              disabled={isExtracting}
              className="mt-3 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              {isExtracting ? 'Извлечение...' : 'Извлечь текст'}
            </button>
          )}
        </div>
      )}

      {/* File upload */}
      {activeTab === 'file' && (
        <div>
          <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-primary-400 transition-colors">
            <Upload className="h-10 w-10 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600 mb-1">
              {selectedFile ? (
                <span className="font-medium text-primary-600">{selectedFile.name}</span>
              ) : (
                'Перетащите файл или нажмите для выбора'
              )}
            </p>
            <p className="text-sm text-gray-400 mb-4">PDF, DOCX — до 50 МБ</p>
            <label className="inline-block bg-primary-600 text-white px-4 py-2 rounded-lg cursor-pointer hover:bg-primary-700 transition-colors text-sm">
              Выбрать файл
              <input type="file" className="hidden" accept=".pdf,.docx" onChange={handleFileChange} />
            </label>
          </div>
          {selectedFile && (
            <button
              type="button"
              onClick={handleExtract}
              disabled={isExtracting}
              className="mt-3 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              {isExtracting ? 'Извлечение...' : 'Извлечь текст из файла'}
            </button>
          )}
        </div>
      )}

      {/* Extracted text preview */}
      {extractedText && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm font-medium text-green-800 mb-1">✓ Текст извлечён</p>
          <p className="text-sm text-green-700 line-clamp-3">{extractedText}</p>
          <p className="text-xs text-green-600 mt-1">{extractedText.length} символов</p>
        </div>
      )}
    </div>
  );

  const renderStep2 = () => (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Настройки подкаста</h2>
      <div className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Название подкаста <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={podcastTitle}
            onChange={(e) => setPodcastTitle(e.target.value)}
            placeholder="Введите название..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Описание (необязательно)
          </label>
          <textarea
            value={podcastDescription}
            onChange={(e) => setPodcastDescription(e.target.value)}
            rows={3}
            placeholder="Краткое описание подкаста..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Стиль подкаста</label>
          <div className="grid grid-cols-3 gap-3">
            {[
              { id: 'entertainment', label: '🎭 Развлекательный', desc: 'Живой, интересный' },
              { id: 'academic', label: '🎓 Академический', desc: 'Серьёзный, глубокий' },
              { id: 'business', label: '💼 Бизнес', desc: 'Профессиональный' },
            ].map((style) => (
              <button
                key={style.id}
                type="button"
                onClick={() => setPodcastStyle(style.id as any)}
                className={`p-3 rounded-lg border text-left transition-colors ${
                  podcastStyle === style.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="font-medium text-sm text-gray-900">{style.label}</div>
                <div className="text-xs text-gray-500 mt-0.5">{style.desc}</div>
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Количество участников
          </label>
          <div className="flex items-center space-x-4">
            {[2, 3, 4].map((n) => (
              <button
                key={n}
                type="button"
                onClick={() => setNumParticipants(n)}
                className={`w-12 h-12 rounded-full border-2 font-semibold transition-colors ${
                  numParticipants === n
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-300 text-gray-600 hover:border-gray-400'
                }`}
              >
                {n}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-1">Рекомендуется 2 участника для начала</p>
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Настройка голосов</h2>
      <div className="space-y-4">
        {participants.map((p, i) => (
          <div key={i} className="bg-gray-50 rounded-xl p-4 border border-gray-200">
            <div className="flex items-center mb-3">
              <div className="bg-primary-100 rounded-full p-2 mr-3">
                <User className="h-4 w-4 text-primary-600" />
              </div>
              <span className="font-medium text-gray-900">Участник {i + 1}</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Имя</label>
                <input
                  type="text"
                  value={p.name}
                  onChange={(e) => updateParticipant(i, 'name', e.target.value)}
                  className="w-full px-2 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-1 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Роль</label>
                <select
                  value={p.role}
                  onChange={(e) => updateParticipant(i, 'role', e.target.value)}
                  className="w-full px-2 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-1 focus:ring-primary-500"
                >
                  {ROLES.map((r) => (
                    <option key={r.id} value={r.id}>{r.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Голос (OpenAI)</label>
                <select
                  value={p.voice_id}
                  onChange={(e) => updateParticipant(i, 'voice_id', e.target.value)}
                  className="w-full px-2 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-1 focus:ring-primary-500"
                >
                  {OPENAI_VOICES.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.name} — {v.desc}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-700">
          💡 Используются голоса OpenAI TTS. Убедитесь, что API ключ настроен в конфигурации.
        </p>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Подтверждение и генерация</h2>

      <div className="space-y-4 mb-6">
        <div className="bg-gray-50 rounded-xl p-4">
          <h3 className="font-medium text-gray-900 mb-3 flex items-center">
            <FileText className="h-4 w-4 mr-2 text-primary-600" />
            Контент
          </h3>
          <p className="text-sm text-gray-600">
            Источник: <span className="font-medium">{activeTab === 'file' ? 'Файл' : activeTab === 'url' ? 'URL' : 'Текст'}</span>
          </p>
          <p className="text-sm text-gray-600">
            Объём: <span className="font-medium">{extractedText.length} символов</span>
          </p>
        </div>

        <div className="bg-gray-50 rounded-xl p-4">
          <h3 className="font-medium text-gray-900 mb-3 flex items-center">
            <Settings className="h-4 w-4 mr-2 text-primary-600" />
            Настройки
          </h3>
          <p className="text-sm text-gray-600">
            Название: <span className="font-medium">{podcastTitle}</span>
          </p>
          <p className="text-sm text-gray-600">
            Стиль: <span className="font-medium capitalize">{podcastStyle}</span>
          </p>
          <p className="text-sm text-gray-600">
            Участников: <span className="font-medium">{numParticipants}</span>
          </p>
        </div>

        <div className="bg-gray-50 rounded-xl p-4">
          <h3 className="font-medium text-gray-900 mb-3 flex items-center">
            <Mic className="h-4 w-4 mr-2 text-primary-600" />
            Участники
          </h3>
          {participants.map((p, i) => (
            <div key={i} className="flex items-center text-sm text-gray-600 mb-1">
              <span className="font-medium mr-2">{p.name}</span>
              <span className="text-gray-400">({p.role})</span>
              <span className="ml-auto text-gray-500">Голос: {p.voice_id}</span>
            </div>
          ))}
        </div>

        <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
          <div className="flex items-start">
            <Clock className="h-4 w-4 text-blue-600 mr-2 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-blue-800">Время генерации</p>
              <p className="text-sm text-blue-700">
                Обычно занимает 2-5 минут. Вы будете перенаправлены на страницу подкаста, где можно отслеживать прогресс.
              </p>
            </div>
          </div>
        </div>
      </div>

      <button
        type="button"
        onClick={handleSubmit}
        disabled={isGenerating}
        className="w-full bg-primary-600 text-white py-3 rounded-xl font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center text-lg"
      >
        {isGenerating ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Создание подкаста...
          </>
        ) : (
          <>
            <Zap className="h-5 w-5 mr-2" />
            Создать подкаст
          </>
        )}
      </button>
    </div>
  );

  const STEP_LABELS = ['Контент', 'Настройки', 'Голоса', 'Генерация'];

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <Link to="/" className="text-gray-500 hover:text-gray-700 text-sm">
          ← Назад
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mt-2">Создать подкаст</h1>
        <p className="text-gray-500 mt-1">Шаг {step} из 4: {STEP_LABELS[step - 1]}</p>
      </div>

      <StepIndicator current={step} total={4} />

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        {step === 1 && renderStep1()}
        {step === 2 && renderStep2()}
        {step === 3 && renderStep3()}
        {step === 4 && renderStep4()}

        {/* Navigation */}
        {step < 4 && (
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-100">
            <button
              type="button"
              onClick={() => setStep((s) => s - 1)}
              disabled={step === 1}
              className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              Назад
            </button>

            <button
              type="button"
              onClick={() => {
                if (step === 1) handleStep1Next();
                else if (step === 2) handleStep2Next();
                else setStep((s) => s + 1);
              }}
              disabled={isExtracting}
              className="flex items-center px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
            >
              {isExtracting ? 'Загрузка...' : 'Далее'}
              <ChevronRight className="h-4 w-4 ml-1" />
            </button>
          </div>
        )}

        {step === 4 && (
          <div className="flex justify-start mt-6 pt-4 border-t border-gray-100">
            <button
              type="button"
              onClick={() => setStep(3)}
              className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              Назад
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CreatePodcastPage;
