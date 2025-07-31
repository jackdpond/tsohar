console.log('Script loaded successfully');

// Load episode content from JSON files
function loadEpisodeContent(series, episode, targetTime = null) {
  console.log('Loading episode content:', series, episode, targetTime);
  
  // Construct the file path using the specified format
  // Replace spaces with underscores but preserve colons
  const safeSeries = series.replace(/ /g, '_').replace(/[&\/]/g, '_');
  const safeEpisode = episode.replace(/ /g, '_');
  const filePath = `Template/${safeSeries}/${safeEpisode}.json`;
  
  // URL encode the file path to handle special characters like ? and &
  // We need to encode the question mark specifically for fetch requests
  const encodedFilePath = filePath.replace(/\?/g, '%3F');
  
  console.log('Fetching file:', filePath);
  
  // Show loading message
  document.getElementById('search-results').innerHTML = '<div>Loading episode...</div>';
  
  fetch(encodedFilePath)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json();
    })
    .then(paragraphs => {
      // Update the main header to show episode information
      const mainTitle = document.querySelector('.main-title');
      
      // Extract episode number and clean title
      const episodeMatch = episode.match(/^Episode \d+:\s*(.+)$/);
      const cleanEpisodeTitle = episodeMatch ? episodeMatch[1] : episode;
      
      // Extract episode number for the series line
      const episodeNumberMatch = episode.match(/^Episode (\d+):/);
      const episodeNumber = episodeNumberMatch ? episodeNumberMatch[1] : '';
      
      mainTitle.innerHTML = `
        <div class="episode-title">${cleanEpisodeTitle}</div>
        <div class="series-name">${series.replace(/_/g, ' ')}, Episode ${episodeNumber}</div>
      `;
      
      let contentHtml = `<div class="transcript-container">`;
      
      paragraphs.forEach((paraObj, index) => {
        const timeId = paraObj.start ? paraObj.start.replace(/:/g, '-') : `para-${index}`;
        const timeDisplay = paraObj.start ? paraObj.start : '';
        const textContent = paraObj.text ? paraObj.text : '';
        
        contentHtml += `
          <div class="transcript-row" id="time-${timeId}" data-start="${paraObj.start || ''}" data-end="${paraObj.end || ''}">
            <div class="timestamp-column">
              ${timeDisplay ? `<span class="timestamp">${timeDisplay}</span>` : ''}
            </div>
            <div class="text-column">
              <p>${textContent}</p>
            </div>
          </div>
        `;
      });
      
      contentHtml += `</div>`;
      document.getElementById('search-results').innerHTML = contentHtml;
      console.log('Episode content loaded successfully');
      
      // If a target time was specified, scroll to that paragraph
      if (targetTime) {
        scrollToParagraph(targetTime);
      }
    })
    .catch(err => {
      console.error('Error loading episode:', err);
      document.getElementById('search-results').innerHTML = `
        <div class="episode-header"><strong>${series}:</strong> ${episode}</div>
        <p style='color:red;'>Could not load episode content: ${err.message}</p>
      `;
    });
}

// Function to reset the header to default state
function resetHeader() {
  const mainTitle = document.querySelector('.main-title');
  mainTitle.innerHTML = 'BibleProject <span class="highlight">Pod-Search</span>';
}

// Function to scroll to a specific paragraph based on time
function scrollToParagraph(targetTime) {
  // Convert target time to the format used in paragraph IDs
  const timeId = targetTime.replace(/:/g, '-');
  const targetElement = document.getElementById(`time-${timeId}`);
  
  if (targetElement) {
    // Scroll to the element with some offset for better visibility
    targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Add a temporary highlight effect to the entire row
    targetElement.style.backgroundColor = '#e3f2fd';
    targetElement.style.transition = 'background-color 0.5s ease';
    
    setTimeout(() => {
      targetElement.style.backgroundColor = '';
    }, 2000);
    
    console.log('Scrolled to paragraph at time:', targetTime);
  } else {
    console.warn('Target paragraph not found for time:', targetTime);
  }
}

// Tab switching functionality
function setupTabs() {
  console.log('Setting up tabs...');
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabPanels = document.querySelectorAll('.tab-panel');
  
  console.log('Found tab buttons:', tabButtons.length);
  console.log('Found tab panels:', tabPanels.length);
  
  tabButtons.forEach(button => {
    console.log('Adding click listener to button:', button.textContent);
    button.addEventListener('click', () => {
      const targetTab = button.getAttribute('data-tab');
      console.log('Tab clicked:', targetTab);
      
      // Update active tab button
      tabButtons.forEach(btn => {
        btn.classList.remove('active');
        console.log('Removed active from button:', btn.textContent);
      });
      button.classList.add('active');
      console.log('Added active to button:', button.textContent);
      
      // Update active tab panel
      tabPanels.forEach(panel => {
        panel.classList.remove('active');
        console.log('Removed active from panel:', panel.id);
      });
      const targetPanel = document.getElementById(`${targetTab}-tab`);
      console.log('Target panel:', targetPanel);
      if (targetPanel) {
        targetPanel.classList.add('active');
        console.log('Added active to panel:', targetPanel.id);
        console.log('Tab switched successfully');
      } else {
        console.error('Target panel not found:', `${targetTab}-tab`);
      }
    });
  });
}

// Text selection popup functionality
function setupTextSelectionPopup() {
  const popup = document.getElementById('selection-popup');
  const searchBtn = document.getElementById('search-selection-btn');
  const copyBtn = document.getElementById('copy-selection-btn');
  let selectedText = '';

  // Handle text selection
  document.addEventListener('mouseup', (e) => {
    const selection = window.getSelection();
    selectedText = selection.toString().trim();
    
    if (selectedText && selectedText.length > 0) {
      // Position the popup near the mouse cursor
      const rect = selection.getRangeAt(0).getBoundingClientRect();
      let left = e.clientX - popup.offsetWidth / 2;
      let top = rect.bottom + window.scrollY + 10;
      
      // Ensure popup stays within viewport
      if (left < 10) left = 10;
      if (left + popup.offsetWidth > window.innerWidth - 10) {
        left = window.innerWidth - popup.offsetWidth - 10;
      }
      if (top + popup.offsetHeight > window.innerHeight + window.scrollY - 10) {
        top = rect.top + window.scrollY - popup.offsetHeight - 10;
      }
      
      popup.style.left = `${left}px`;
      popup.style.top = `${top}px`;
      popup.style.display = 'block';
    } else {
      popup.style.display = 'none';
    }
  });

  // Hide popup when clicking outside
  document.addEventListener('mousedown', (e) => {
    if (!popup.contains(e.target)) {
      popup.style.display = 'none';
    }
  });

  // Search button functionality
  searchBtn.addEventListener('click', () => {
    if (selectedText) {
      // Switch to search tab
      const searchTab = document.querySelector('[data-tab="search"]');
      if (searchTab) {
        searchTab.click();
      }
      
      // Set the search input value
      const searchInput = document.getElementById('sidebar-search-input');
      if (searchInput) {
        searchInput.value = selectedText;
        searchInput.focus();
        
        // Trigger the search
        const searchBtn = document.getElementById('sidebar-search-btn');
        if (searchBtn) {
          searchBtn.click();
        }
      }
      
      popup.style.display = 'none';
    }
  });

  // Copy button functionality
  copyBtn.addEventListener('click', () => {
    if (selectedText) {
      navigator.clipboard.writeText(selectedText).then(() => {
        // Show a brief visual feedback
        const originalText = copyBtn.textContent;
        copyBtn.textContent = '✅ Copied!';
        setTimeout(() => {
          copyBtn.textContent = originalText;
        }, 1000);
      }).catch(err => {
        console.error('Failed to copy text: ', err);
      });
      
      popup.style.display = 'none';
    }
  });
}

// Sidebar resizer functionality
function setupSidebarResizer() {
  const resizer = document.querySelector('.sidebar-resizer');
  const sidebar = document.querySelector('.sidebar');
  let isResizing = false;
  let startX = 0;
  let startWidth = 0;

  const minWidth = 200;
  const maxWidth = 600;

  function startResize(e) {
    isResizing = true;
    startX = e.clientX;
    startWidth = parseInt(getComputedStyle(sidebar).getPropertyValue('--sidebar-width'));
    
    document.addEventListener('mousemove', resize);
    document.addEventListener('mouseup', stopResize);
    
    // Prevent text selection during resize
    e.preventDefault();
  }

  function resize(e) {
    if (!isResizing) return;
    
    const deltaX = e.clientX - startX;
    let newWidth = startWidth + deltaX;
    
    // Constrain width
    newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
    
    // Update CSS custom property for both sidebar and main content
    sidebar.style.setProperty('--sidebar-width', `${newWidth}px`);
    
    // Also update the main content area to ensure it moves with the sidebar
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
      mainContent.style.marginLeft = `${newWidth}px`;
      mainContent.style.width = `calc(100vw - ${newWidth}px)`;
    }
  }

  function stopResize() {
    isResizing = false;
    document.removeEventListener('mousemove', resize);
    document.removeEventListener('mouseup', stopResize);
  }

  resizer.addEventListener('mousedown', startResize);
}

// Search functionality for sidebar
function setupSidebarSearch(seriesData) {
  const sidebarSearchInput = document.getElementById('sidebar-search-input');
  const sidebarSearchBtn = document.getElementById('sidebar-search-btn');
  const sidebarSearchResults = document.getElementById('sidebar-search-results');
  
  async function performSidebarSearch() {
    const query = sidebarSearchInput.value.trim();
    if (!query) {
      sidebarSearchResults.innerHTML = '';
      return;
    }
    
    // Show loading indicator
    sidebarSearchResults.innerHTML = '<div style="color: #666; padding: 8px;">Searching...</div>';
    
    try {
      const results = await searchEpisodes(query, seriesData);
      renderSidebarSearchResults(results, sidebarSearchResults);
    } catch (error) {
      console.error('Search failed:', error);
      sidebarSearchResults.innerHTML = '<div style="color: red; padding: 8px;">Search failed. Please try again.</div>';
    }
  }
  
  sidebarSearchBtn.addEventListener('click', performSidebarSearch);
  sidebarSearchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      performSidebarSearch();
    }
  });
}

function renderSidebarSearchResults(results, container) {
  if (results.length === 0) {
    container.innerHTML = '<div style="color: #666; padding: 8px;">No results found.</div>';
    return;
  }
  
  container.innerHTML = results.map(r => {
    // Handle both old format (series, episode) and new format (from Index.search)
    const series = r.series || r.series_title;
    const episode = r.episode || r.episode_title;
    const similarity = r.similarity_score ? ` (${(r.similarity_score * 100).toFixed(1)}%)` : '';
    const text = r.text ? ` - "${r.text.substring(0, 100)}${r.text.length > 100 ? '...' : ''}"` : '';
    const time = r.start ? ` [${r.start}]` : '';
    
    return `<div class="sidebar-search-result" data-series="${series}" data-episode="${episode}" data-time="${r.start || ''}">
      <strong>${series.replace(/_/g, ' ')}:</strong> ${episode}${time}${similarity}
      <div style="font-size: 0.9em; color: #666; margin-top: 2px;">${text}</div>
    </div>`;
  }).join('');
  
  // Add click handlers
  container.querySelectorAll('.sidebar-search-result').forEach(el => {
    el.addEventListener('click', () => {
      const series = el.getAttribute('data-series');
      const episode = el.getAttribute('data-episode');
      const time = el.getAttribute('data-time');
      loadEpisodeContent(series, episode, time);
    });
  });
}

// Search episodes function using the Index API
async function searchEpisodes(query, data) {
  if (!query.trim()) {
    return [];
  }
  
  try {
    const response = await fetch(`http://localhost:5001/search?q=${encodeURIComponent(query)}&k=10`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const results = await response.json();
    return results;
  } catch (error) {
    console.error('Search error:', error);
    // Fallback to the old search method if API is not available
    const results = [];
    Object.entries(data).forEach(([series, episodes]) => {
      episodes.forEach(ep => {
        if (ep.toLowerCase().includes(query.toLowerCase())) {
          results.push({ series, episode: ep });
        }
      });
    });
    return results;
  }
}

// Load seriesData and initialize the site
fetch('seriesData.json')
  .then(response => response.json())
  .then(seriesData => {
    console.log('Series data loaded:', Object.keys(seriesData));
    renderSidebar(seriesData);
    setupTabs();
    setupSidebarSearch(seriesData);
    setupTextSelectionPopup(); // Initialize text selection popup
    setupSidebarResizer(); // Initialize sidebar resizer
    resetHeader(); // Reset header on page load
    
    // Initialize main content positioning to match sidebar width
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    if (sidebar && mainContent) {
      const sidebarWidth = getComputedStyle(sidebar).getPropertyValue('--sidebar-width');
      mainContent.style.marginLeft = sidebarWidth;
      mainContent.style.width = `calc(100vw - ${sidebarWidth})`;
    }
  })
  .catch(error => {
    console.error('Error loading series data:', error);
  });

// DOM elements
const seriesNav = document.getElementById('series-nav');
const searchResults = document.getElementById('search-results');

function renderSidebar(data) {
  console.log('Rendering sidebar');
  seriesNav.innerHTML = '';
  
  Object.entries(data).forEach(([series, episodes]) => {
    const seriesDiv = document.createElement('div');
    seriesDiv.className = 'series';
    seriesDiv.textContent = series.replace(/_/g, ' ');
    seriesDiv.tabIndex = 0;
    seriesDiv.setAttribute('aria-expanded', 'false');

    const episodeList = document.createElement('ul');
    episodeList.className = 'episodes';
    episodeList.style.display = 'none';

    episodes.forEach(ep => {
      const epLi = document.createElement('li');
      epLi.className = 'episode';
      epLi.textContent = ep;
      epLi.tabIndex = 0;
      
      // Click handler that loads episode content
      epLi.addEventListener('click', function() {
        console.log('Episode clicked:', series, ep);
        loadEpisodeContent(series, ep);
      });
      
      episodeList.appendChild(epLi);
    });

    seriesDiv.addEventListener('click', function() {
      const expanded = seriesDiv.getAttribute('aria-expanded') === 'true';
      seriesDiv.setAttribute('aria-expanded', !expanded);
      episodeList.style.display = expanded ? 'none' : 'block';
    });

    seriesNav.appendChild(seriesDiv);
    seriesNav.appendChild(episodeList);
  });
} 