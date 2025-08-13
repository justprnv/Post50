(function() {
  // Theme - Set default to light mode and ensure immediate application
  function applyTheme() {
    const root = document.documentElement;
    const savedTheme = localStorage.getItem('theme') || 'light';
    root.setAttribute('data-theme', savedTheme);
    
    // Update toggle button state
    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) {
      if (savedTheme === 'dark') {
        themeBtn.classList.add('active');
        themeBtn.setAttribute('aria-checked', 'true');
      } else {
        themeBtn.classList.remove('active');
        themeBtn.setAttribute('aria-checked', 'false');
      }
    }
  }

  // Apply theme immediately when script loads
  applyTheme();

  // Theme toggle functionality
  const themeBtn = document.getElementById('themeToggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const root = document.documentElement;
      const current = root.getAttribute('data-theme') || 'light';
      const next = current === 'light' ? 'dark' : 'light';
      
      // Apply theme immediately
      root.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      
      // Update toggle state
      if (next === 'dark') {
        themeBtn.classList.add('active');
        themeBtn.setAttribute('aria-checked', 'true');
      } else {
        themeBtn.classList.remove('active');
        themeBtn.setAttribute('aria-checked', 'false');
      }
      
      // Update user's theme preference in database if logged in
      if (window.IS_AUTHENTICATED) {
        updateUserThemePreference(next);
      }
    });
  }

  // Function to update user's theme preference in database
  async function updateUserThemePreference(theme) {
    try {
      const response = await fetch('/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `theme=${theme}`
      });
      
      if (response.ok) {
        console.log('Theme preference updated in database');
      }
    } catch (error) {
      console.error('Error updating theme preference:', error);
    }
  }

  // Ensure theme persists across page loads
  document.addEventListener('DOMContentLoaded', function() {
    applyTheme();
    
    // Sync theme with user settings if logged in
    if (window.IS_AUTHENTICATED) {
      loadUserThemePreference();
    }
  });

  // Also apply theme when page becomes visible (for better persistence)
  document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
      applyTheme();
    }
  });

  // Function to sync theme with user settings
  function syncThemeWithUserSettings() {
    // This would ideally fetch the user's theme preference from the server
    // For now, we'll rely on localStorage, but you can extend this
    const savedTheme = localStorage.getItem('theme') || 'light';
    const root = document.documentElement;
    
    if (root.getAttribute('data-theme') !== savedTheme) {
      root.setAttribute('data-theme', savedTheme);
    }
  }

  // Function to load user's theme preference from database
  async function loadUserThemePreference() {
    try {
      const response = await fetch('/api/user/theme');
      if (response.ok) {
        const data = await response.json();
        if (data.theme && data.theme !== 'system') {
          localStorage.setItem('theme', data.theme);
          applyTheme();
        }
      }
    } catch (error) {
      console.error('Error loading user theme preference:', error);
    }
  }

  // Initialize toggle switches
  function initToggleSwitches() {
    const toggles = document.querySelectorAll('.theme-toggle[role="switch"]');
    toggles.forEach(toggle => {
      const setting = toggle.id.replace('Toggle', '');
      const saved = localStorage.getItem(setting);
      if (saved === 'true') {
        toggle.classList.add('active');
        toggle.setAttribute('aria-checked', 'true');
      }
      
      toggle.addEventListener('click', () => {
        const isActive = toggle.classList.contains('active');
        toggle.classList.toggle('active');
        toggle.setAttribute('aria-checked', !isActive);
        localStorage.setItem(setting, !isActive);
      });
    });
  }

  // Registration validation
  const usernameInput = document.getElementById('username');
  const emailInput = document.getElementById('email');
  const usernameHint = document.getElementById('usernameHint');
  const emailHint = document.getElementById('emailHint');

  if (usernameInput) {
    let usernameTimeout;
    usernameInput.addEventListener('input', () => {
      clearTimeout(usernameTimeout);
      usernameTimeout = setTimeout(() => {
        const username = usernameInput.value.trim();
        if (username.length < 3) {
          usernameHint.textContent = 'Username must be at least 3 characters';
          usernameHint.style.color = 'var(--danger)';
        } else {
          fetch(`/api/check_username?username=${encodeURIComponent(username)}`)
            .then(response => response.json())
            .then(data => {
              if (data.available) {
                usernameHint.textContent = '✓ Username available';
                usernameHint.style.color = 'var(--success)';
              } else {
                usernameHint.textContent = '✗ Username already taken';
                usernameHint.style.color = 'var(--danger)';
              }
            })
            .catch(error => {
              console.error('Error checking username:', error);
            });
        }
      }, 300);
    });
  }

  if (emailInput) {
    let emailTimeout;
    emailInput.addEventListener('input', () => {
      clearTimeout(emailTimeout);
      emailTimeout = setTimeout(() => {
        const email = emailInput.value.trim();
        if (email && !email.includes('@')) {
          emailHint.textContent = 'Please enter a valid email address';
          emailHint.style.color = 'var(--danger)';
        } else if (email) {
          fetch(`/api/check_email?email=${encodeURIComponent(email)}`)
            .then(response => response.json())
            .then(data => {
              if (data.available) {
                emailHint.textContent = '✓ Email available';
                emailHint.style.color = 'var(--success)';
              } else {
                emailHint.textContent = '✗ Email already registered';
                emailHint.style.color = 'var(--danger)';
              }
            })
            .catch(error => {
              console.error('Error checking email:', error);
            });
        }
      }, 300);
    });
  }

  // Post loading
  let page = 1;
  let loading = false;
  const loadMoreBtn = document.getElementById('loadMoreBtn');

  async function loadMorePosts() {
    if (loading) return;
    loading = true;
    loadMoreBtn.textContent = 'Loading...';
    
    try {
      const response = await fetch(`/api/posts?page=${page + 1}`);
      const data = await response.json();
      
      if (data.items && data.items.length > 0) {
        data.items.forEach(post => {
          const postElement = createPostElement(post);
          document.getElementById('postsFeed').appendChild(postElement);
        });
        page++;
      } else {
        loadMoreBtn.style.display = 'none';
      }
    } catch (error) {
      console.error('Error loading posts:', error);
    } finally {
      loading = false;
      loadMoreBtn.textContent = 'Load More Posts';
    }
  }

  function createPostElement(post) {
    const template = document.getElementById('postItemTemplate');
    const clone = template.content.cloneNode(true);
    
    clone.querySelector('.post-card').setAttribute('data-post-id', post.id);
    clone.querySelector('.post-title').innerHTML = post.title;
    clone.querySelector('.post-content').innerHTML = post.content;
    
    // Create clickable author link
    const authorSpan = clone.querySelector('.post-author');
    authorSpan.innerHTML = `By <a href="/u/${post.author_id}" class="author-link">${post.author}</a>`;
    
    clone.querySelector('.post-date').textContent = new Date(post.created_at).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
    
    if (post.image_url) {
      const img = clone.querySelector('.post-image');
      img.src = post.image_url;
      img.style.display = 'block';
    }
    
    if (post.tags && post.tags.length > 0) {
      const tagsContainer = clone.querySelector('.post-tags');
      post.tags.forEach(tag => {
        const tagSpan = document.createElement('span');
        tagSpan.className = 'tag';
        tagSpan.textContent = `#${tag}`;
        tagsContainer.appendChild(tagSpan);
      });
    }
    
    // Set up vote buttons
    const upvoteBtn = clone.querySelector('[data-vote-type="up"]');
    const downvoteBtn = clone.querySelector('[data-vote-type="down"]');
    upvoteBtn.onclick = () => votePost(post.id, 'up');
    downvoteBtn.onclick = () => votePost(post.id, 'down');
    
    return clone;
  }

  // Voting
  async function votePost(postId, voteType) {
    if (!window.IS_AUTHENTICATED) {
      alert('Please log in to vote');
      return;
    }
    
    try {
      const response = await fetch(`/post/${postId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ post_id: postId, vote_type: voteType })
      });
      
      if (response.ok) {
        const data = await response.json();
        const postCard = document.querySelector(`[data-post-id="${postId}"]`);
        if (postCard) {
          postCard.querySelector('[data-vote-type="up"] .score').textContent = data.upvotes;
          postCard.querySelector('[data-vote-type="down"] .score').textContent = data.downvotes;
        }
      }
    } catch (error) {
      console.error('Error voting:', error);
    }
  }

  // Comments
  function toggleComments(postId) {
    const commentsSection = document.getElementById(`comments-${postId}`);
    if (commentsSection) {
      commentsSection.style.display = commentsSection.style.display === 'none' ? 'block' : 'none';
    }
  }

  async function addComment(event, postId) {
    event.preventDefault();
    if (!window.IS_AUTHENTICATED) {
      alert('Please log in to comment');
      return;
    }
    
    const input = event.target.querySelector('input');
    const content = input.value.trim();
    if (!content) return;
    
    try {
      const response = await fetch('/post/comment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ post_id: postId, content: content })
      });
      
      if (response.ok) {
        const data = await response.json();
        const commentsSection = document.getElementById(`comments-${postId}`);
        const commentDiv = document.createElement('div');
        commentDiv.className = 'comment';
        commentDiv.innerHTML = `<strong>${data.author}</strong>: ${data.content}`;
        commentsSection.insertBefore(commentDiv, event.target);
        input.value = '';
        
        // Update comment count
        const commentCount = commentsSection.parentElement.querySelector('.comment-count');
        if (commentCount) {
          commentCount.textContent = parseInt(commentCount.textContent) + 1;
        }
      }
    } catch (error) {
      console.error('Error adding comment:', error);
    }
  }

  // Post deletion
  async function deletePost(postId) {
    if (!confirm('Are you sure you want to delete this post?')) {
      return;
    }
    
    try {
      const response = await fetch(`/post/${postId}/delete`, { method: 'POST' });
      if (response.ok) {
        const postCard = document.querySelector(`[data-post-id="${postId}"]`);
        if (postCard) {
          postCard.remove();
        }
      }
    } catch (error) {
      console.error('Error deleting post:', error);
    }
  }

  // Rich text editor
  function formatText(command) {
    document.execCommand(command, false, null);
  }

  function formatTitle(command) {
    document.execCommand(command, false, null);
  }

  function insertList() {
    document.execCommand('insertUnorderedList', false, null);
  }

  function insertLink() {
    const url = prompt('Enter URL:');
    if (url) {
      document.execCommand('createLink', false, url);
    }
  }

  function insertImage() {
    const url = prompt('Enter image URL:');
    if (url) {
      document.execCommand('insertImage', false, url);
    }
  }

  // Auto-save drafts
  let autoSaveTimeout;
  const editor = document.getElementById('editor');
  const contentInput = document.getElementById('content');
  const titleEditor = document.getElementById('titleEditor');
  const titleInput = document.getElementById('title');
  
  if (editor && contentInput) {
    editor.addEventListener('input', () => {
      clearTimeout(autoSaveTimeout);
      autoSaveTimeout = setTimeout(() => {
        contentInput.value = editor.innerHTML;
        localStorage.setItem('postDraft', editor.innerHTML);
      }, 1000);
    });
    
    // Load draft on page load only if editing
    const draft = localStorage.getItem('postDraft');
    if (draft && !editor.innerHTML.trim() && !window.location.pathname.includes('/edit')) {
      editor.innerHTML = draft;
      contentInput.value = draft;
    }
  }

  if (titleEditor && titleInput) {
    titleEditor.addEventListener('input', () => {
      titleInput.value = titleEditor.innerHTML;
    });
  }

  // Initialize everything
  initToggleSwitches();
  
  // Make functions globally available
  window.votePost = votePost;
  window.toggleComments = toggleComments;
  window.addComment = addComment;
  window.deletePost = deletePost;
  window.loadMorePosts = loadMorePosts;
  window.formatText = formatText;
  window.formatTitle = formatTitle;
  window.insertList = insertList;
  window.insertLink = insertLink;
  window.insertImage = insertImage;
})();
