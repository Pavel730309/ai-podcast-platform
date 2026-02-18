import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Mic, Plus } from 'lucide-react';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);
  const location = useLocation();

  const isActive = (path: string) =>
    location.pathname === path ? 'text-primary-600 font-semibold' : 'text-gray-600 hover:text-primary-600';

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="bg-primary-600 p-2 rounded-lg group-hover:bg-primary-700 transition-colors">
              <Mic className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">AI Podcast Studio</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link to="/" className={`transition-colors font-medium text-sm ${isActive('/')}`}>
              Мои подкасты
            </Link>
            <Link
              to="/create"
              className="inline-flex items-center bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors"
            >
              <Plus className="h-4 w-4 mr-1.5" />
              Создать подкаст
            </Link>
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-600 hover:text-gray-900 focus:outline-none p-1"
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <div className="flex flex-col space-y-2">
              <Link
                to="/"
                className="text-gray-600 hover:text-primary-600 transition-colors font-medium py-2 px-2 rounded-lg hover:bg-gray-50"
                onClick={() => setIsMenuOpen(false)}
              >
                Мои подкасты
              </Link>
              <Link
                to="/create"
                className="inline-flex items-center bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                <Plus className="h-4 w-4 mr-1.5" />
                Создать подкаст
              </Link>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
