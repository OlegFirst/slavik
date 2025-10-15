/**
 * Interactive Diagram Viewer
 * Enables full-screen viewing of Mermaid diagrams with zoom and pan functionality
 */

class DiagramViewer {
  constructor() {
    this.modal = null;
    this.currentDiagram = null;
    this.scale = 1;
    this.minScale = 0.5;
    this.maxScale = 5;
    this.scaleStep = 0.1;  // Reduced from 0.25 to 0.1 for smoother zoom
    this.isPanning = false;
    this.startX = 0;
    this.startY = 0;
    this.translateX = 0;
    this.translateY = 0;

    this.init();
  }

  init() {
    // Create modal structure
    this.createModal();

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.attachDiagramListeners());
    } else {
      this.attachDiagramListeners();
    }
  }

  createModal() {
    // Create modal HTML
    const modalHTML = `
      <div id="diagram-viewer-modal" class="diagram-viewer-modal">
        <div class="diagram-viewer-content">
          <div class="diagram-viewer-controls">
            <button class="diagram-viewer-btn" id="zoom-in" title="Zoom In (+)">+</button>
            <button class="diagram-viewer-btn" id="zoom-out" title="Zoom Out (-)">−</button>
            <button class="diagram-viewer-btn reset" id="reset-view" title="Reset View (R)">↻</button>
            <button class="diagram-viewer-btn close" id="close-viewer" title="Close (Esc)">×</button>
          </div>
          <div class="diagram-viewer-zoom-info" id="zoom-info">100%</div>
          <div class="diagram-viewer-instructions">
            <kbd>+</kbd>/<kbd>-</kbd> Zoom · <kbd>Drag</kbd> Pan · <kbd>R</kbd> Reset · <kbd>Esc</kbd> Close
          </div>
          <div class="diagram-viewer-container" id="diagram-container">
            <div id="diagram-content"></div>
          </div>
        </div>
      </div>
    `;

    // Add to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Get modal reference
    this.modal = document.getElementById('diagram-viewer-modal');
    this.container = document.getElementById('diagram-container');
    this.content = document.getElementById('diagram-content');
    this.zoomInfo = document.getElementById('zoom-info');

    // Attach modal event listeners
    this.attachModalListeners();
  }

  attachModalListeners() {
    // Close button
    document.getElementById('close-viewer').addEventListener('click', () => this.close());

    // Zoom buttons
    document.getElementById('zoom-in').addEventListener('click', () => this.zoom(1));
    document.getElementById('zoom-out').addEventListener('click', () => this.zoom(-1));
    document.getElementById('reset-view').addEventListener('click', () => this.resetView());

    // Click outside to close
    this.modal.addEventListener('click', (e) => {
      if (e.target === this.modal) {
        this.close();
      }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (!this.modal.classList.contains('active')) return;

      switch(e.key) {
        case 'Escape':
          this.close();
          break;
        case '+':
        case '=':
          e.preventDefault();
          this.zoom(1);
          break;
        case '-':
        case '_':
          e.preventDefault();
          this.zoom(-1);
          break;
        case 'r':
        case 'R':
          e.preventDefault();
          this.resetView();
          break;
      }
    });

    // Mouse wheel zoom
    this.container.addEventListener('wheel', (e) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -1 : 1;
      this.zoom(delta);
    }, { passive: false });

    // Pan functionality
    this.container.addEventListener('mousedown', (e) => this.startPan(e));
    this.container.addEventListener('mousemove', (e) => this.pan(e));
    this.container.addEventListener('mouseup', () => this.endPan());
    this.container.addEventListener('mouseleave', () => this.endPan());

    // Touch support for mobile
    this.container.addEventListener('touchstart', (e) => this.startPan(e.touches[0]));
    this.container.addEventListener('touchmove', (e) => {
      e.preventDefault();
      this.pan(e.touches[0]);
    }, { passive: false });
    this.container.addEventListener('touchend', () => this.endPan());
  }

  attachDiagramListeners() {
    // Find all Mermaid diagrams and add click listeners
    const diagrams = document.querySelectorAll('.mermaid, .mermaid-container pre.mermaid');

    diagrams.forEach((diagram) => {
      diagram.addEventListener('click', (e) => {
        e.preventDefault();
        this.open(diagram);
      });

      // Make sure the diagram has pointer cursor
      diagram.style.cursor = 'pointer';
    });

    console.log(`DiagramViewer: Initialized with ${diagrams.length} diagrams`);
  }

  open(diagramElement) {
    // Clone the diagram
    const clone = diagramElement.cloneNode(true);

    // Clear previous content
    this.content.innerHTML = '';
    this.content.appendChild(clone);

    // Find the SVG element
    const svg = this.content.querySelector('svg');
    if (svg) {
      svg.classList.add('diagram-viewer-svg');
      svg.style.maxWidth = 'none';
      svg.style.maxHeight = 'none';

      // Store original dimensions
      this.originalWidth = svg.getAttribute('width') || svg.getBBox().width;
      this.originalHeight = svg.getAttribute('height') || svg.getBBox().height;
    }

    // Reset view
    this.resetView();

    // Show modal
    this.modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  close() {
    this.modal.classList.remove('active');
    document.body.style.overflow = '';
    this.content.innerHTML = '';
  }

  zoom(direction) {
    const newScale = this.scale + (direction * this.scaleStep);

    if (newScale >= this.minScale && newScale <= this.maxScale) {
      this.scale = newScale;
      this.updateTransform();
      this.updateZoomInfo();
    }
  }

  resetView() {
    this.scale = 1;
    this.translateX = 0;
    this.translateY = 0;
    this.updateTransform();
    this.updateZoomInfo();

    // Reset scroll position
    this.container.scrollTop = 0;
    this.container.scrollLeft = 0;
  }

  startPan(e) {
    this.isPanning = true;
    this.startX = e.clientX - this.translateX;
    this.startY = e.clientY - this.translateY;
    this.container.style.cursor = 'grabbing';
  }

  pan(e) {
    if (!this.isPanning) return;

    e.preventDefault();
    this.translateX = e.clientX - this.startX;
    this.translateY = e.clientY - this.startY;
    this.updateTransform();
  }

  endPan() {
    this.isPanning = false;
    this.container.style.cursor = 'grab';
  }

  updateTransform() {
    const svg = this.content.querySelector('svg');
    if (svg) {
      svg.style.transform = `scale(${this.scale}) translate(${this.translateX / this.scale}px, ${this.translateY / this.scale}px)`;
    }
  }

  updateZoomInfo() {
    this.zoomInfo.textContent = `${Math.round(this.scale * 100)}%`;
  }
}

// Initialize when script loads
if (typeof window !== 'undefined') {
  window.diagramViewer = new DiagramViewer();
  console.log('DiagramViewer: Loaded successfully');
}
