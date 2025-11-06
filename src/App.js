import React, { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your AI assistant. Describe your product idea and I\'ll help you create a structured Product Requirements Document (PRD). What would you like to build?'
    }
  ]);
  const [input, setInput] = useState('');
  const [prdContent, setPrdContent] = useState({
    title: '',
    overview: '',
    objectives: [],
    features: [],
    requirements: [],
    userStories: []
  });
  const [isGenerating, setIsGenerating] = useState(false);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsGenerating(true);

    try {
      // Call your FastAPI backend with RAG system
      const response = await fetch('/api/process-prd', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: currentInput,
          conversation_history: messages.map(msg => ({
            role: msg.type === 'user' ? 'user' : 'assistant',
            content: msg.content
          }))
        })
      });

      const result = await response.json();

      if (result.success) {
        // Update PRD content with AI-generated sections
        // This directly populates your existing prdContent state structure
        setPrdContent(prev => ({
          ...prev,
          title: result.prd_content.title || prev.title || 'Product Requirements Document',
          overview: result.prd_content.overview || prev.overview || 'Product overview will be generated...',
          objectives: result.prd_content.objectives && result.prd_content.objectives.length > 0 
            ? result.prd_content.objectives 
            : prev.objectives,
          features: result.prd_content.features && result.prd_content.features.length > 0 
            ? result.prd_content.features 
            : prev.features,
          requirements: result.prd_content.requirements && result.prd_content.requirements.length > 0 
            ? result.prd_content.requirements 
            : prev.requirements,
          userStories: result.prd_content.userStories && result.prd_content.userStories.length > 0 
            ? result.prd_content.userStories 
            : prev.userStories
        }));

        // Create AI response with clarifying questions
        let aiResponse = "I've analyzed your product idea and updated the PRD! ";
        
        // Count how many sections were updated
        const updatedSections = [];
        if (result.prd_content.title) updatedSections.push('title');
        if (result.prd_content.overview) updatedSections.push('overview');
        if (result.prd_content.objectives?.length > 0) updatedSections.push('objectives');
        if (result.prd_content.features?.length > 0) updatedSections.push('features');
        if (result.prd_content.requirements?.length > 0) updatedSections.push('requirements');
        if (result.prd_content.userStories?.length > 0) updatedSections.push('user stories');
        
        if (updatedSections.length > 0) {
          aiResponse += `I've updated the ${updatedSections.join(', ')} sections. `;
        }
        
        if (result.clarifying_questions && result.clarifying_questions.length > 0) {
          aiResponse += "\n\nTo make the PRD even better, could you help me with these questions:\n";
          result.clarifying_questions.forEach((q, i) => {
            aiResponse += `\n${i + 1}. ${q}`;
          });
        } else {
          aiResponse += "The PRD looks comprehensive based on your input! Feel free to provide more details or ask me to refine any section.";
        }

        const assistantMessage = {
          id: messages.length + 2,
          type: 'assistant',
          content: aiResponse
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // Handle error from RAG system
        const errorMessage = {
          id: messages.length + 2,
          type: 'assistant',
          content: `I encountered an issue processing your request: ${result.error_message || 'Unknown error'}. Please try rephrasing your product idea.`
        };
        setMessages(prev => [...prev, errorMessage]);
      }

    } catch (error) {
      console.error('Error calling PRD API:', error);
      const errorMessage = {
        id: messages.length + 2,
        type: 'assistant',
        content: 'I encountered a technical error connecting to the AI system. Please check your connection and try again.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleExportPRD = () => {
    // Create markdown content
    let markdown = `# ${prdContent.title || 'Product Requirements Document'}\n\n`;
    markdown += `*Generated: ${new Date().toLocaleString()}*\n\n`;
    markdown += `---\n\n`;
    
    // Overview Section
    markdown += `## Overview\n\n`;
    markdown += `${prdContent.overview || 'No overview provided yet.'}\n\n`;
    
    // Objectives Section
    markdown += `## Objectives\n\n`;
    if (prdContent.objectives.length > 0) {
      prdContent.objectives.forEach(objective => {
        markdown += `- ${objective}\n`;
      });
    } else {
      markdown += `*No objectives defined yet.*\n`;
    }
    markdown += `\n`;
    
    // Key Features Section
    markdown += `## Key Features\n\n`;
    if (prdContent.features.length > 0) {
      prdContent.features.forEach(feature => {
        markdown += `- ${feature}\n`;
      });
    } else {
      markdown += `*No features defined yet.*\n`;
    }
    markdown += `\n`;
    
    // Technical Requirements Section
    markdown += `## Technical Requirements\n\n`;
    if (prdContent.requirements.length > 0) {
      prdContent.requirements.forEach(requirement => {
        markdown += `- ${requirement}\n`;
      });
    } else {
      markdown += `*No technical requirements defined yet.*\n`;
    }
    markdown += `\n`;
    
    // User Stories Section
    markdown += `## User Stories\n\n`;
    if (prdContent.userStories.length > 0) {
      prdContent.userStories.forEach(story => {
        markdown += `- ${story}\n`;
      });
    } else {
      markdown += `*No user stories defined yet.*\n`;
    }
    markdown += `\n`;
    
    markdown += `---\n\n`;
    markdown += `*This document was generated using the PRD Generator AI Assistant*\n`;
    
    // Create blob and download
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Generate filename with sanitized title and timestamp
    const sanitizedTitle = (prdContent.title || 'PRD')
      .replace(/[^a-z0-9]/gi, '_')
      .toLowerCase();
    const timestamp = new Date().toISOString().split('T')[0];
    link.download = `${sanitizedTitle}_${timestamp}.md`;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Left Side - Chat Interface */}
      <div className="w-1/2 flex flex-col bg-white border-r border-gray-300">
        {/* Chat Header */}
        <div className="bg-blue-600 text-white p-4 shadow-sm">
          <h1 className="text-lg font-semibold">PRD Generator AI Assistant</h1>
          <p className="text-blue-100 text-sm">Describe your product idea and I'll help structure it</p>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                <p className="text-sm">{message.content}</p>
              </div>
            </div>
          ))}
          
          {isGenerating && (
            <div className="flex justify-start">
              <div className="bg-gray-200 text-gray-800 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                  <p className="text-sm">Analyzing and updating PRD...</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex space-x-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Describe your product features, requirements, or user needs..."
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows="3"
            />
            <button
              onClick={handleSendMessage}
              disabled={!input.trim() || isGenerating}
              className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </div>

      {/* Right Side - Generated PRD */}
      <div className="w-1/2 flex flex-col bg-gray-50">
        {/* PRD Header */}
        <div className="bg-green-600 text-white p-4 shadow-sm">
          <h2 className="text-lg font-semibold">Generated PRD</h2>
          <p className="text-green-100 text-sm">Live document updated as you chat</p>
        </div>

        {/* PRD Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
            {/* Title Section */}
            <div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                {prdContent.title || 'Product Requirements Document'}
              </h3>
              <div className="text-sm text-gray-500">
                Last updated: {new Date().toLocaleString()}
              </div>
            </div>

            {/* Overview Section */}
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Overview</h4>
              <p className="text-gray-600 leading-relaxed">
                {prdContent.overview || 'Start chatting to generate your product overview...'}
              </p>
            </div>

            {/* Objectives Section */}
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Objectives</h4>
              {prdContent.objectives.length > 0 ? (
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {prdContent.objectives.map((objective, index) => (
                    <li key={index}>{objective}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-400 italic">Objectives will appear here as you describe your goals...</p>
              )}
            </div>

            {/* Features Section */}
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Key Features</h4>
              {prdContent.features.length > 0 ? (
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {prdContent.features.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-400 italic">Features will be extracted from your conversations...</p>
              )}
            </div>

            {/* Requirements Section */}
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Technical Requirements</h4>
              {prdContent.requirements.length > 0 ? (
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {prdContent.requirements.map((requirement, index) => (
                    <li key={index}>{requirement}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-400 italic">Technical requirements will be identified automatically...</p>
              )}
            </div>

            {/* User Stories Section */}
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-2">User Stories</h4>
              {prdContent.userStories.length > 0 ? (
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {prdContent.userStories.map((story, index) => (
                    <li key={index}>{story}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-400 italic">User stories will be generated from your descriptions...</p>
              )}
            </div>
          </div>

          {/* Export Button */}
          <div className="mt-6">
            <button 
              onClick={handleExportPRD}
              className="w-full bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center space-x-2"
            >
              <svg 
                className="w-5 h-5" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" 
                />
              </svg>
              <span>Export PRD as Markdown</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
