import React, { useState } from 'react';
import { BookOpen, Brain, Trophy, Send, RefreshCw, HelpCircle, ChevronRight, Target, TrendingUp, FileText } from 'lucide-react';
import './App.css';

// const API_URL = 'http://localhost:8000';
const API_URL = 'http://127.0.0.1:8000';


export default function App() {
  const [userId, setUserId] = useState(null);
  const [topic, setTopic] = useState('');
  const [goal, setGoal] = useState('');
  const [currentLevel, setCurrentLevel] = useState(3);
  const [isLearning, setIsLearning] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Learning state
  const [explanation, setExplanation] = useState('');
  const [quiz, setQuiz] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [materials, setMaterials] = useState([]);
  const [progress, setProgress] = useState(null);
  const [understandingLevel, setUnderstandingLevel] = useState(0);
  const [activeTab, setActiveTab] = useState('lesson');
  
  // Start learning session
  const startLearning = async () => {
    if (!topic || !goal) {
      alert('Please enter both topic and learning goal');
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/start_learning`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          learning_goal: goal,
          current_level: currentLevel
        })
      });
      
      const data = await response.json();
      setUserId(data.user_id);
      setIsLearning(true);
      
      if (data.explanation) {
        setExplanation(data.explanation);
      }
      if (data.quiz) {
        setQuiz(data.quiz);
      }
      if (data.materials) {
        setMaterials(data.materials);
      }
      
      fetchProgress(data.user_id);
    } catch (error) {
      console.error('Error starting session:', error);
      alert('Failed to connect to backend. Make sure the API is running on port 8000');
    } finally {
      setLoading(false);
    }
  };
  
  // Submit quiz answer
  // const submitAnswer = async () => {
  //   if (!userAnswer.trim()) return;
    
  //   setLoading(true);
  //   try {
  //     const response = await fetch(`${API_URL}/submit_answer`, {
  //       method: 'POST',
  //       headers: { 'Content-Type': 'application/json' },
  //       body: JSON.stringify({
  //         user_id: userId,
  //         answer: userAnswer
  //       })
  //     });
      
  //     const data = await response.json();
  //     setFeedback(data.evaluation);
  //     setUnderstandingLevel(data.new_understanding_level);
      
  //     if (data.next_content) {
  //       if (data.next_content.tutor_explanation) {
  //         setExplanation(data.next_content.tutor_explanation);
  //       }
  //       if (data.next_content.current_quiz) {
  //         setQuiz(data.next_content.current_quiz);
  //         setUserAnswer('');
  //         setFeedback(null);
  //       }
  //     }
      
  //     fetchProgress(userId);
  //   } catch (error) {
  //     console.error('Error submitting answer:', error);
  //   } finally {
  //     setLoading(false);
  //   }
  // };
  const submitAnswer = async () => {
    if (!userAnswer.trim()) return;
    console.log('Submitting answer:', userAnswer);
    console.log('To question:', quiz.question);
    
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/submit_answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          answer: userAnswer
        })
      });
      
      const data = await response.json();
      
      // ADD THESE DEBUG LINES
      console.log('Backend response:', data);
      console.log('Evaluation:', data.evaluation);
      console.log('New quiz:', data.next_content);
      
      // Set the feedback - THIS IS THE KEY LINE
      if (data.evaluation) {
        setFeedback(data.evaluation);
        console.log('Feedback set to:', data.evaluation);
      }
      
      setUnderstandingLevel(data.new_understanding_level);
      
      // Update quiz if new one provided
      if (data.next_content && data.next_content.current_quiz) {
        setQuiz(data.next_content.current_quiz);
        setUserAnswer(''); // Clear previous answer
        // Don't clear feedback immediately - let user see it
        // setFeedback(null); // COMMENT THIS OUT if it exists
      }
      
      fetchProgress(userId);
    } catch (error) {
      console.error('Error submitting answer:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Get help
  const getHelp = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/get_help/${userId}`, {
        method: 'POST'
      });
      
      const data = await response.json();
      if (data.explanation) {
        setExplanation(data.explanation);
      }
      if (data.materials) {
        setMaterials([...materials, ...data.materials]);
      }
    } catch (error) {
      console.error('Error getting help:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Fetch progress
  const fetchProgress = async (uid) => {
    try {
      const response = await fetch(`${API_URL}/progress/${uid || userId}`);
      const data = await response.json();
      setProgress(data);
      setUnderstandingLevel(data.understanding_level);
    } catch (error) {
      console.error('Error fetching progress:', error);
    }
  };
  
  const resetSession = () => {
    setUserId(null);
    setIsLearning(false);
    setExplanation('');
    setQuiz(null);
    setFeedback(null);
    setMaterials([]);
    setProgress(null);
    setUserAnswer('');
    setTopic('');
    setGoal('');
    setCurrentLevel(3);
  };
  
  if (!isLearning) {
    return (
      <div className="app-container">
        <div className="welcome-card">
          <div className="card-header">
            <Brain className="icon" />
            <h1>AI Learning Assistant</h1>
          </div>
          
          <div className="card-content">
            <div className="form-group">
              <label>What do you want to learn?</label>
              <input
                type="text"
                placeholder="e.g., Machine Learning, Python, Calculus..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="input"
              />
            </div>
            
            <div className="form-group">
              <label>What's your specific goal?</label>
              <input
                type="text"
                placeholder="e.g., Understand gradient descent, Build a web app..."
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                className="input"
              />
            </div>
            
            <div className="form-group">
              <label>Current Knowledge Level: {currentLevel}/10</label>
              <input
                type="range"
                min="0"
                max="10"
                value={currentLevel}
                onChange={(e) => setCurrentLevel(parseInt(e.target.value))}
                className="slider"
              />
              <div className="slider-labels">
                <span>Beginner</span>
                <span>Intermediate</span>
                <span>Expert</span>
              </div>
            </div>
            
            <button
              onClick={startLearning}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? (
                <>
                  <RefreshCw className="icon-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <ChevronRight />
                  Start Learning Journey
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="learning-container">
      {/* Header */}
      <div className="header">
        <div className="header-content">
          <div>
            <h1>
              <Brain className="icon" />
              Learning: {topic}
            </h1>
            <p className="goal">
              <Target className="icon-small" />
              Goal: {goal}
            </p>
          </div>
          <button onClick={resetSession} className="btn-outline">
            New Session
          </button>
        </div>
        
        <div className="progress-section">
          <div className="progress-label">
            <span>Understanding Level</span>
            <span className="progress-value">{understandingLevel.toFixed(1)}/10</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${understandingLevel * 10}%` }}
            />
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="main-content">
        <div className="content-left">
          {/* Tabs */}
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'lesson' ? 'active' : ''}`}
              onClick={() => setActiveTab('lesson')}
            >
              <BookOpen className="icon-small" />
              Lesson
            </button>
            <button
              className={`tab ${activeTab === 'quiz' ? 'active' : ''}`}
              onClick={() => setActiveTab('quiz')}
            >
              <Brain className="icon-small" />
              Quiz
            </button>
            <button
              className={`tab ${activeTab === 'materials' ? 'active' : ''}`}
              onClick={() => setActiveTab('materials')}
            >
              <FileText className="icon-small" />
              Materials
            </button>
          </div>
          
          {/* Tab Content */}
          <div className="tab-content">
            {activeTab === 'lesson' && (
              <div className="card">
                <h2>Current Explanation</h2>
                {explanation ? (
                  <div>
                    <div className="explanation-box">
                      {explanation.split('\n').map((paragraph, i) => (
                        <p key={i}>{paragraph}</p>
                      ))}
                    </div>
                    <button
                      onClick={getHelp}
                      className="btn-outline"
                      disabled={loading}
                    >
                      <HelpCircle className="icon-small" />
                      Still Confused? Get Different Explanation
                    </button>
                  </div>
                ) : (
                  <p className="empty-state">
                    No explanation available yet. Start with a quiz or request help.
                  </p>
                )}
              </div>
            )}
            
            {activeTab === 'quiz' && (
              <div className="card">
                <h2>Knowledge Check</h2>
                {quiz && (
                  <div className="quiz-section">
                    <div className="question-box">
                      <p>{quiz.question}</p>
                    </div>
                    
                    {quiz.options ? (
                      <div className="options-grid">
                        {quiz.options.map((option, i) => (
                          <button
                            key={i}
                            onClick={() => setUserAnswer(option)}
                            className={`option-btn ${userAnswer === option ? 'selected' : ''}`}
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                    ) : (
                      <textarea
                        className="answer-input"
                        rows={4}
                        placeholder="Type your answer here..."
                        value={userAnswer}
                        onChange={(e) => setUserAnswer(e.target.value)}
                      />
                    )}
                    
                    <button
                      onClick={submitAnswer}
                      disabled={loading || !userAnswer}
                      className="btn-primary"
                    >
                      <Send className="icon-small" />
                      Submit Answer
                    </button>
                  </div>
                )}
                
                {feedback && (
                  <div className={`feedback-box ${feedback.correct ? 'correct' : 'incorrect'}`}>
                    <p className="feedback-title">
                      {feedback.correct ? '✅ Correct!' : '❌ Not quite right'}
                    </p>
                    <p>{feedback.feedback}</p>
                    {feedback.misconceptions && feedback.misconceptions.length > 0 && (
                      <div>
                        <p className="feedback-subtitle">Areas to review:</p>
                        <ul>
                          {feedback.misconceptions.map((m, i) => (
                            <li key={i}>{m}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
            
            {activeTab === 'materials' && (
              <div className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <h2>Learning Resources</h2>
                  <button 
                    onClick={async () => {
                      const response = await fetch(`${API_URL}/refresh_materials/${userId}`, { method: 'POST' });
                      const data = await response.json();
                      setMaterials(data.materials);
                    }}
                    className="btn-outline"
                    style={{ fontSize: '14px', padding: '8px 16px' }}
                  >
                    🔄 Get New Materials
                  </button>
                </div>
                
                {materials.length > 0 ? (
                  <div className="materials-list">
                    {materials.map((material, i) => (
                      <div key={i} className="material-item">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                          <h3>{material.title}</h3>
                          <span style={{ 
                            background: material.type === 'video' ? '#ff6b6b' : 
                                       material.type === 'tutorial' ? '#4ecdc4' : 
                                       material.type === 'article' ? '#45b7d1' : '#96ceb4',
                            color: 'white',
                            padding: '2px 8px',
                            borderRadius: '4px',
                            fontSize: '12px'
                          }}>
                            {material.type}
                          </span>
                        </div>
                        <p>{material.content}</p>
                        <a
                          href={material.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="material-link"
                        >
                          View Resource →
                        </a>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="empty-state">
                    Loading learning materials...
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* Right Sidebar */}
        <div className="content-right">
          <div className="card">
            <h3>
              <Trophy className="icon-small" />
              Your Progress
            </h3>
            {progress && (
              <div className="stats">
                <div className="stat-item">
                  <span>Quiz Attempts</span>
                  <span className="stat-value">{progress.quiz_count}</span>
                </div>
                <div className="stat-item">
                  <span>Materials Reviewed</span>
                  <span className="stat-value">{progress.materials_reviewed}</span>
                </div>
                
                {progress.progress_analysis && (
                  <>
                    <div className="analysis-section">
                      <h4>
                        <TrendingUp className="icon-small" />
                        Strengths
                      </h4>
                      <ul>
                        {progress.progress_analysis.strengths?.map((s, i) => (
                          <li key={i}>{s}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="analysis-section">
                      <h4>
                        <Target className="icon-small" />
                        Focus Areas
                      </h4>
                      <ul>
                        {progress.progress_analysis.improvements_needed?.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}