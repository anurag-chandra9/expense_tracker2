// ExpenseChart Component
function ExpenseChart() {
    const [chartData, setChartData] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    const chartRef = React.useRef(null);
    let chartInstance = React.useRef(null);

    const loadChartData = () => {
        setLoading(true);
        fetch('/api/expenses/chart/')
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch chart data');
                return response.json();
            })
            .then(data => {
                setChartData(data);
                if (chartRef.current) {
                    if (chartInstance.current) {
                        chartInstance.current.destroy();
                    }

                    const ctx = chartRef.current.getContext('2d');
                    chartInstance.current = new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: Object.keys(data).map(key => {
                                const label = key.toLowerCase().replace(/_/g, ' ');
                                return label.charAt(0).toUpperCase() + label.slice(1);
                            }),
                            datasets: [{
                                data: Object.values(data),
                                backgroundColor: [
                                    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD'
                                ],
                                borderWidth: 2
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'bottom',
                                    labels: {
                                        padding: 20,
                                        font: {
                                            size: 12
                                        }
                                    }
                                },
                                title: {
                                    display: true,
                                    text: 'Expense Distribution',
                                    font: {
                                        size: 16,
                                        weight: 'bold'
                                    },
                                    padding: {
                                        top: 10,
                                        bottom: 30
                                    }
                                }
                            }
                        }
                    });
                }
                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    };

    React.useEffect(() => {
        loadChartData();
        // Set up interval to refresh chart data every 30 seconds
        const interval = setInterval(loadChartData, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return (
        <div className="chart-container text-center" style={{ height: '400px' }}>
            <div className="d-flex justify-content-center align-items-center h-100">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                </div>
            </div>
        </div>
    );

    if (error) return (
        <div className="chart-container">
            <div className="alert alert-danger" role="alert">
                {error}
            </div>
        </div>
    );

    return (
        <div className="chart-container" style={{ height: '400px' }}>
            <canvas ref={chartRef}></canvas>
        </div>
    );
}

// ExpenseForm Component
function ExpenseForm() {
    const [formData, setFormData] = React.useState({
        title: '',
        amount: '',
        date: '',
        category: 'FOOD'
    });
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState(null);
    const [success, setSuccess] = React.useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess(false);

        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
        fetch('/api/expenses/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to add expense');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                setSuccess(true);
                setFormData({
                    title: '',
                    amount: '',
                    date: '',
                    category: 'FOOD'
                });
                // Refresh the page after 1.5 seconds
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            }
        })
        .catch(err => {
            setError(err.message);
        })
        .finally(() => {
            setLoading(false);
        });
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    return (
        <div className="expense-form">
            {error && (
                <div className="alert alert-danger" role="alert">
                    {error}
                </div>
            )}
            {success && (
                <div className="alert alert-success" role="alert">
                    Expense added successfully!
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label className="form-label">Title</label>
                    <input
                        type="text"
                        name="title"
                        className="form-control"
                        value={formData.title}
                        onChange={handleChange}
                        required
                        disabled={loading}
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Amount</label>
                    <input
                        type="number"
                        name="amount"
                        className="form-control"
                        value={formData.amount}
                        onChange={handleChange}
                        required
                        step="0.01"
                        min="0"
                        disabled={loading}
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Date</label>
                    <input
                        type="date"
                        name="date"
                        className="form-control"
                        value={formData.date}
                        onChange={handleChange}
                        required
                        disabled={loading}
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Category</label>
                    <select
                        name="category"
                        className="form-control"
                        value={formData.category}
                        onChange={handleChange}
                        disabled={loading}
                    >
                        <option value="FOOD">Food</option>
                        <option value="TRAVEL">Travel</option>
                        <option value="BILLS">Bills</option>
                        <option value="ENTERTAINMENT">Entertainment</option>
                        <option value="OTHER">Other</option>
                    </select>
                </div>
                <button 
                    type="submit" 
                    className="btn btn-primary w-100" 
                    disabled={loading}
                >
                    {loading ? (
                        <>
                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                            Adding...
                        </>
                    ) : 'Add Expense'}
                </button>
            </form>
        </div>
    );
}

// TotalExpenses Component
function TotalExpenses() {
    const [total, setTotal] = React.useState(0);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);

    const loadTotalData = () => {
        setLoading(true);
        fetch('/api/expenses/total/')
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch total');
                return response.json();
            })
            .then(data => {
                setTotal(data.total);
                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    };

    React.useEffect(() => {
        loadTotalData();
        // Set up interval to refresh total data every 30 seconds
        const interval = setInterval(loadTotalData, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return (
        <div className="total-expenses text-center">
            <h2>Total Expenses</h2>
            <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
            </div>
        </div>
    );

    if (error) return (
        <div className="total-expenses">
            <div className="alert alert-danger" role="alert">
                {error}
            </div>
        </div>
    );

    return (
        <div className="total-expenses">
            <h2>Total Expenses</h2>
            <div className="total-amount">${total.toFixed(2)}</div>
            <button 
                className="btn btn-primary mt-3" 
                onClick={() => window.bootstrap.Modal.getOrCreateInstance(document.getElementById('addExpenseModal')).show()}
            >
                Add New Expense
            </button>
        </div>
    );
}

// Update total expenses
function updateTotalExpenses() {
    fetch('/api/expenses/total/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const totalElement = document.getElementById('totalExpenses');
            if (totalElement && data.total !== undefined) {
                const formattedTotal = new Intl.NumberFormat('en-IN', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(data.total);
                totalElement.textContent = formattedTotal;
            }
        })
        .catch(error => {
            console.error('Error fetching total:', error);
            const totalElement = document.getElementById('totalExpenses');
            if (totalElement) {
                totalElement.textContent = 'Error';
            }
        });
}

// Call immediately and set up interval
document.addEventListener('DOMContentLoaded', function() {
    updateTotalExpenses();
    setInterval(updateTotalExpenses, 30000); // Update every 30 seconds
});

// Custom Alert Event Handler
window.addEventListener('showAlert', function(e) {
    const { message, type } = e.detail;
    
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    
    // Add message
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Find or create messages container
    let messagesContainer = document.querySelector('.messages');
    if (!messagesContainer) {
        messagesContainer = document.createElement('div');
        messagesContainer.className = 'messages mb-4';
        document.querySelector('.container').insertBefore(messagesContainer, document.querySelector('.container').firstChild);
    }
    
    // Add alert to container
    messagesContainer.appendChild(alertDiv);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
        if (messagesContainer.children.length === 0) {
            messagesContainer.remove();
        }
    }, 5000);
});
