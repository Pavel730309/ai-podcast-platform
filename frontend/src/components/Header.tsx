import React from 'react';
import { Link } from 'react-router-dom';
import { Menu, X, Mic, Play, FileText, Podcast } from 'lucide-react';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="bg-primary-600 p-2 rounded-lg">
              <Mic className="h-6 w-6 text-white" />
            </div>
            <Link to="/" className="text-xl font-bold text-gray-900">
              AI Podcast Studio
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              to="/" 
              className="text-gray-600 hover:text-primary-600 transition-colors font-medium"
            >
              Home
            </Link>
            <Link 
              to="/create" 
              className="text-gray-600 hover:text-primary-600 transition-colors font-medium"
            >
              Create Podcast
            </Link>
            <Link 
              to="/podcasts" 
              className="text-gray-600 hover:text-primary-600 transition-colors font-medium"
            >
              My Podcasts
            </Link>
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-600 hover:text-gray-900 focus:outline-none"
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <div className="flex flex-col space-y-3">
              <Link 
                to="/" 
                className="text-gray-600 hover:text-primary-600 transition-colors font-medium py-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Home
              </Link>
              <Link 
                to="/create" 
                className="text-gray-600 hover:text-primary-600 transition-colors font-medium py-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Create Podcast
              </Link>
              <Link 
                to="/podcasts" 
                className="text-gray-600 hover:text-primary-600 transition-colors font-medium py-2"
                onClick={() => setIsMenuOpen(false)}
              >
                My Podcasts
              </Link>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;