// Dashboard Interactivity - Chart Click Filtering
class DashboardInteractivity {
    constructor() {
        this.currentFilters = this.parseUrlParams();
        this.initializeEventListeners();
    }

    // Parse URL parameters to get current filters
    parseUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        return {
            date_range: urlParams.get('date_range') || 'all',
            role: urlParams.get('role') || 'all',
            home_id: urlParams.get('home_id') || '',
            user_id: urlParams.get('user_id') || ''
        };
    }

    // Initialize event listeners for chart interactions
    initializeEventListeners() {
        // Listen for chart click events
        document.addEventListener('chartClicked', (event) => {
            this.handleChartClick(event.detail);
        });

        // Listen for filter updates
        document.addEventListener('filtersUpdated', (event) => {
            this.updateAllPanels(event.detail);
        });

        // Initialize chart click handlers after charts are rendered
        setTimeout(() => {
            this.attachChartClickHandlers();
        }, 1000);
    }

    // Handle chart element clicks
    handleChartClick(clickData) {
        console.log('Chart clicked:', clickData);

        // Update filters based on click
        let newFilters = { ...this.currentFilters };

        switch (clickData.type) {
            case 'role':
                newFilters.role = clickData.value;
                break;
            case 'home':
                newFilters.home_id = clickData.value;
                break;
            case 'user':
                newFilters.user_id = clickData.value;
                break;
            case 'date':
                // Handle date-based clicks (could be weekly/monthly groupings)
                newFilters.date_range = 'custom';
                newFilters.start_date = clickData.start_date;
                newFilters.end_date = clickData.end_date;
                break;
        }

        // Apply new filters
        this.applyFilters(newFilters);
    }

    // Apply filters and update all dashboard panels
    applyFilters(filters) {
        this.currentFilters = filters;

        // Update URL with new filters
        this.updateUrl(filters);

        // Update all dashboard panels
        this.updateAllPanels(filters);

        // Update filter form
        this.updateFilterForm(filters);
    }

    // Update URL with current filters
    updateUrl(filters) {
        const url = new URL(window.location);

        // Clear existing params
        url.search = '';

        // Add new filter params
        Object.keys(filters).forEach(key => {
            if (filters[key] && filters[key] !== 'all' && filters[key] !== '') {
                url.searchParams.set(key, filters[key]);
            }
        });

        // Update browser history without reload
        window.history.pushState({}, '', url);
    }

    // Update filter form to reflect current state
    updateFilterForm(filters) {
        const form = document.getElementById('filters-form');
        if (!form) return;

        Object.keys(filters).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'select-one') {
                    input.value = filters[key];
                } else {
                    input.value = filters[key];
                }
            }
        });

        // Handle custom date range visibility
        const customRange = document.getElementById('custom-date-range');
        if (customRange) {
            customRange.style.display = filters.date_range === 'custom' ? 'block' : 'none';
        }
    }

    // Update all dashboard panels with new data
    async updateAllPanels(filters) {
        try {
            // Show loading state
            this.showLoadingState();

            // Get current page to determine which APIs to call
            const currentPage = window.location.pathname;

            // Build query string from filters
            const queryString = new URLSearchParams(filters).toString();

            // Update metrics (for all pages)
            await this.updateMetrics(queryString);

            // Update page-specific content
            switch (currentPage) {
                case '/':
                    await this.updateHomePage(queryString);
                    break;
                case '/signup-funnel':
                    await this.updateSignupFunnelPage(queryString);
                    break;
                case '/user-engagement':
                    await this.updateUserEngagementPage(queryString);
                    break;
                case '/acquisition':
                    await this.updateAcquisitionPage(queryString);
                    break;
                case '/task-analysis':
                    await this.updateTaskAnalysisPage(queryString);
                    break;
                case '/feature-usage':
                    await this.updateFeatureUsagePage(queryString);
                    break;
                case '/drop-off-analysis':
                    await this.updateDropOffAnalysisPage(queryString);
                    break;
            }

            // Hide loading state
            this.hideLoadingState();

            // Re-attach chart click handlers
            setTimeout(() => {
                this.attachChartClickHandlers();
            }, 500);

        } catch (error) {
            console.error('Error updating panels:', error);
            this.hideLoadingState();
        }
    }

    // Update metrics panel
    async updateMetrics(queryString) {
        try {
            const response = await fetch(`/api/metrics?${queryString}`);
            const data = await response.json();

            // Update metric displays
            const totalUsersEl = document.querySelector('[data-metric="total_users"]');
            const newUsersEl = document.querySelector('[data-metric="new_users"]');

            if (totalUsersEl) totalUsersEl.textContent = data.total_users?.toLocaleString() || '0';
            if (newUsersEl) newUsersEl.textContent = data.new_users?.toLocaleString() || '0';

        } catch (error) {
            console.error('Error updating metrics:', error);
        }
    }

    // Update home page content
    async updateHomePage(queryString) {
        try {
            // Update growth trend chart
            const growthResponse = await fetch(`/api/growth-trend?${queryString}`);
            const growthData = await growthResponse.json();
            this.updateGrowthTrendChart(growthData);

            // Update user distribution chart
            const distributionResponse = await fetch(`/api/user-distribution?${queryString}`);
            const distributionData = await distributionResponse.json();
            this.updateUserDistributionChart(distributionData);

        } catch (error) {
            console.error('Error updating home page:', error);
        }
    }

    // Update signup funnel page
    async updateSignupFunnelPage(queryString) {
        try {
            const response = await fetch(`/api/signup-funnel?${queryString}`);
            const data = await response.json();
            this.updateSignupFunnelCharts(data);
        } catch (error) {
            console.error('Error updating signup funnel page:', error);
        }
    }

    // Update user engagement page
    async updateUserEngagementPage(queryString) {
        try {
            const response = await fetch(`/api/user-engagement?${queryString}`);
            const data = await response.json();
            this.updateUserEngagementCharts(data);
        } catch (error) {
            console.error('Error updating user engagement page:', error);
        }
    }

    // Update acquisition page
    async updateAcquisitionPage(queryString) {
        try {
            const response = await fetch(`/api/acquisition?${queryString}`);
            const data = await response.json();
            this.updateAcquisitionCharts(data);
        } catch (error) {
            console.error('Error updating acquisition page:', error);
        }
    }

    // Update task analysis page
    async updateTaskAnalysisPage(queryString) {
        try {
            const response = await fetch(`/api/task-analysis?${queryString}`);
            const data = await response.json();
            this.updateTaskAnalysisCharts(data);
        } catch (error) {
            console.error('Error updating task analysis page:', error);
        }
    }

    // Update feature usage page
    async updateFeatureUsagePage(queryString) {
        try {
            const response = await fetch(`/api/feature-usage?${queryString}`);
            const data = await response.json();
            this.updateFeatureUsageCharts(data);
        } catch (error) {
            console.error('Error updating feature usage page:', error);
        }
    }

    // Update drop-off analysis page
    async updateDropOffAnalysisPage(queryString) {
        try {
            const response = await fetch(`/api/drop-off-analysis?${queryString}`);
            const data = await response.json();
            this.updateDropOffAnalysisCharts(data);
        } catch (error) {
            console.error('Error updating drop-off analysis page:', error);
        }
    }

    // Chart update methods
    updateGrowthTrendChart(data) {
        // Update Chart.js chart if it exists
        const chartCanvas = document.getElementById('growthTrendChart');
        if (chartCanvas && window.growthTrendChart) {
            window.growthTrendChart.data.datasets[0].data = data.map(d => d.dau);
            window.growthTrendChart.data.labels = data.map(d => d.date);
            window.growthTrendChart.update();
        }
    }

    updateUserDistributionChart(data) {
        const chartCanvas = document.getElementById('userDistributionChart');
        if (chartCanvas && window.userDistributionChart) {
            window.userDistributionChart.data.datasets[0].data = data.map(d => d.count);
            window.userDistributionChart.data.labels = data.map(d => d.role);
            window.userDistributionChart.update();
        }
    }

    updateSignupFunnelCharts(data) {
        // Update signup funnel visualization
        // This would be implemented based on your specific chart library
        console.log('Updating signup funnel charts with:', data);
    }

    updateUserEngagementCharts(data) {
        // Update engagement charts
        console.log('Updating user engagement charts with:', data);
    }

    updateAcquisitionCharts(data) {
        // Update acquisition charts
        console.log('Updating acquisition charts with:', data);
    }

    updateTaskAnalysisCharts(data) {
        // Update task analysis charts
        console.log('Updating task analysis charts with:', data);
    }

    updateFeatureUsageCharts(data) {
        // Update feature usage charts
        console.log('Updating feature usage charts with:', data);
    }

    updateDropOffAnalysisCharts(data) {
        // Update drop-off analysis charts
        console.log('Updating drop-off analysis charts with:', data);
    }

    // Attach click handlers to chart elements
    attachChartClickHandlers() {
        // This will be called after charts are rendered
        // Attach event listeners to clickable chart elements

        // Example for Chart.js charts
        const charts = ['growthTrendChart', 'userDistributionChart', 'signupFunnelChart'];

        charts.forEach(chartId => {
            const chartCanvas = document.getElementById(chartId);
            if (chartCanvas && window[chartId]) {
                chartCanvas.onclick = (event) => {
                    const chart = window[chartId];
                    const activeElement = chart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, false);

                    if (activeElement.length > 0) {
                        const dataIndex = activeElement[0].index;
                        const dataset = chart.data.datasets[activeElement[0].datasetIndex];
                        const label = chart.data.labels[dataIndex];
                        const value = dataset.data[dataIndex];

                        // Determine click type based on chart
                        let clickType = 'unknown';
                        if (chartId === 'userDistributionChart') {
                            clickType = 'role';
                        }

                        // Dispatch custom event
                        this.handleChartClick({
                            type: clickType,
                            value: label,
                            data: value,
                            chartId: chartId
                        });
                    }
                };
            }
        });
    }

    // Loading state management
    showLoadingState() {
        // Add loading overlay or spinners
        const loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'dashboard-loading';
        loadingOverlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        loadingOverlay.innerHTML = `
            <div class="bg-white rounded-lg p-6 flex items-center space-x-4">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span class="text-gray-700">Updating dashboard...</span>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
    }

    hideLoadingState() {
        const loadingOverlay = document.getElementById('dashboard-loading');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
    }

    // Quick filter methods
    filterByRole(role) {
        this.applyFilters({ ...this.currentFilters, role: role });
    }

    filterByHome(homeId) {
        this.applyFilters({ ...this.currentFilters, home_id: homeId });
    }

    filterByUser(userId) {
        this.applyFilters({ ...this.currentFilters, user_id: userId });
    }

    filterByDateRange(dateRange, startDate = null, endDate = null) {
        const newFilters = { ...this.currentFilters, date_range: dateRange };
        if (dateRange === 'custom' && startDate && endDate) {
            newFilters.start_date = startDate;
            newFilters.end_date = endDate;
        }
        this.applyFilters(newFilters);
    }
}

// Initialize dashboard interactivity when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.dashboardInteractivity = new DashboardInteractivity();

    // Global helper functions for charts to trigger filtering
    window.filterByRole = (role) => window.dashboardInteractivity.filterByRole(role);
    window.filterByHome = (homeId) => window.dashboardInteractivity.filterByHome(homeId);
    window.filterByUser = (userId) => window.dashboardInteractivity.filterByUser(userId);
    window.filterByDateRange = (dateRange, startDate, endDate) =>
        window.dashboardInteractivity.filterByDateRange(dateRange, startDate, endDate);
});