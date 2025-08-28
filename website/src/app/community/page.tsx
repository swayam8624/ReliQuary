'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowLeftIcon,
  ChatBubbleLeftRightIcon,
  UserGroupIcon,
  LightBulbIcon,
  ExclamationCircleIcon,
  QuestionMarkCircleIcon,
  LinkIcon,
  ArrowUpIcon,
  HeartIcon,
  ChatBubbleLeftIcon
} from '@heroicons/react/24/outline';
import Link from 'next/link';

export default function CommunityPage() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [newPost, setNewPost] = useState({ title: '', content: '', category: 'general' });

  const categories = [
    { id: 'all', name: 'All Topics', icon: ChatBubbleLeftRightIcon },
    { id: 'general', name: 'General', icon: UserGroupIcon },
    { id: 'ideas', name: 'Ideas', icon: LightBulbIcon },
    { id: 'support', name: 'Support', icon: QuestionMarkCircleIcon },
    { id: 'bugs', name: 'Bugs', icon: ExclamationCircleIcon },
  ];

  const posts = [
    {
      id: 1,
      title: 'Welcome to the ReliQuary Community!',
      content: 'This is our new community forum where developers can discuss ReliQuary, share ideas, and get help from both the community and our team.',
      author: 'ReliQuary Team',
      category: 'general',
      replies: 24,
      likes: 42,
      timestamp: '2 hours ago',
      isPinned: true
    },
    {
      id: 2,
      title: 'Best practices for implementing zero-knowledge proofs?',
      content: 'I\'m working on integrating ZK proofs into my application and would love to hear about best practices from others who have done this.',
      author: 'CryptoDev',
      category: 'support',
      replies: 8,
      likes: 15,
      timestamp: '5 hours ago',
      isPinned: false
    },
    {
      id: 3,
      title: 'Feature Request: Webhook support for consensus events',
      content: 'It would be great to have webhook notifications for consensus decisions. This would help us integrate more seamlessly with our existing systems.',
      author: 'EnterpriseUser',
      category: 'ideas',
      replies: 12,
      likes: 28,
      timestamp: '1 day ago',
      isPinned: false
    },
    {
      id: 4,
      title: 'Bug: API key creation failing in dashboard',
      content: 'When trying to create a new API key in the customer dashboard, the request times out after 30 seconds. Others experiencing this?',
      author: 'DevUser',
      category: 'bugs',
      replies: 5,
      likes: 7,
      timestamp: '1 day ago',
      isPinned: false
    }
  ];

  const handleNewPost = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real implementation, this would submit to an API
    alert('Post created! It will appear in the forum shortly.');
    setNewPost({ title: '', content: '', category: 'general' });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center space-x-2">
              <ArrowLeftIcon className="h-5 w-5 text-gray-600" />
              <span className="text-sm font-medium text-gray-600">Back to Home</span>
            </Link>
            <h1 className="text-xl font-semibold text-gray-900">Community Forum</h1>
            <div></div> {/* Spacer for alignment */}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-8">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold text-gray-900 mb-4"
          >
            ReliQuary Community
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xl text-gray-600 max-w-3xl mx-auto"
          >
            Connect with other developers, share ideas, and get help from the community and ReliQuary team.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Categories</h2>
              <nav className="space-y-1">
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setActiveCategory(category.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      activeCategory === category.id
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <category.icon className="h-5 w-5" />
                    <span>{category.name}</span>
                  </button>
                ))}
              </nav>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Community Resources</h2>
              <ul className="space-y-3">
                <li>
                  <Link href="/docs" className="flex items-center text-gray-600 hover:text-primary-600">
                    <LinkIcon className="h-4 w-4 mr-2" />
                    <span>Documentation</span>
                  </Link>
                </li>
                <li>
                  <Link href="/support" className="flex items-center text-gray-600 hover:text-primary-600">
                    <QuestionMarkCircleIcon className="h-4 w-4 mr-2" />
                    <span>Support Center</span>
                  </Link>
                </li>
                <li>
                  <a href="https://discord.gg/reliquary" className="flex items-center text-gray-600 hover:text-primary-600">
                    <ChatBubbleLeftRightIcon className="h-4 w-4 mr-2" />
                    <span>Discord Chat</span>
                  </a>
                </li>
                <li>
                  <a href="https://github.com/reliquary" className="flex items-center text-gray-600 hover:text-primary-600">
                    <LinkIcon className="h-4 w-4 mr-2" />
                    <span>GitHub</span>
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* New Post Form */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Create New Post</h2>
              <form onSubmit={handleNewPost}>
                <div className="mb-4">
                  <input
                    type="text"
                    value={newPost.title}
                    onChange={(e) => setNewPost({...newPost, title: e.target.value})}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Post title"
                    required
                  />
                </div>
                
                <div className="mb-4">
                  <textarea
                    value={newPost.content}
                    onChange={(e) => setNewPost({...newPost, content: e.target.value})}
                    rows={3}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                    placeholder="What would you like to discuss?"
                    required
                  />
                </div>
                
                <div className="flex justify-between items-center">
                  <select
                    value={newPost.category}
                    onChange={(e) => setNewPost({...newPost, category: e.target.value})}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="general">General</option>
                    <option value="ideas">Ideas</option>
                    <option value="support">Support</option>
                    <option value="bugs">Bugs</option>
                  </select>
                  
                  <button
                    type="submit"
                    className="btn-primary"
                  >
                    Post to Community
                  </button>
                </div>
              </form>
            </div>

            {/* Forum Posts */}
            <div className="space-y-4">
              {posts
                .filter(post => activeCategory === 'all' || post.category === activeCategory)
                .map((post) => (
                <motion.div
                  key={post.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow ${
                    post.isPinned ? 'ring-2 ring-primary-100' : ''
                  }`}
                >
                  {post.isPinned && (
                    <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 mb-3">
                      <ArrowUpIcon className="h-3 w-3 mr-1" />
                      Pinned
                    </div>
                  )}
                  
                  <div className="flex justify-between">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{post.title}</h3>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      {post.category}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-4">{post.content}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-500">
                        by <span className="font-medium">{post.author}</span> • {post.timestamp}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <button className="flex items-center text-gray-500 hover:text-primary-600">
                        <HeartIcon className="h-4 w-4 mr-1" />
                        <span className="text-sm">{post.likes}</span>
                      </button>
                      <button className="flex items-center text-gray-500 hover:text-primary-600">
                        <ChatBubbleLeftIcon className="h-4 w-4 mr-1" />
                        <span className="text-sm">{post.replies}</span>
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Community Guidelines */}
            <div className="mt-8 bg-blue-50 rounded-xl border border-blue-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Community Guidelines</h2>
              <ul className="list-disc list-inside space-y-2 text-gray-600">
                <li>Be respectful and constructive in all interactions</li>
                <li>Search before posting to avoid duplicates</li>
                <li>Keep discussions on topic and relevant</li>
                <li>Share knowledge and help others when possible</li>
                <li>Report inappropriate content to moderators</li>
              </ul>
              <p className="mt-3 text-gray-600">
                By participating, you agree to our{' '}
                <Link href="/terms" className="text-primary-600 hover:text-primary-700">
                  Community Code of Conduct
                </Link>
                .
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}