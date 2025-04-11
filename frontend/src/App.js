import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [products, setProducts] = useState([]);
  const [filters, setFilters] = useState({
    limit: 10,
    update: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [taskId, setTaskId] = useState(null);

  // Обработчик изменения полей формы
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFilters({ ...filters, [name]: type === 'checkbox' ? checked : value });
  };

  // Загрузка товаров из базы данных при монтировании компонента
  useEffect(() => {
    const loadProducts = async () => {
      try {
        const response = await axios.get('/api/products/', {
          params: { load_products: true }, // Параметр для загрузки товаров из БД
        });
        setProducts(response.data);
      } catch (err) {
        setError('Ошибка при загрузке товаров из базы данных');
        console.error(err);
      }
    };

    loadProducts();
  }, []);

  // Запуск задачи Celery через API
  const fetchProducts = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get('/api/products/', {
        params: filters, // Передаем параметры фильтрации
      });
      setTaskId(response.data.task_id); // Сохраняем task_id для отслеживания статуса
    } catch (err) {
      setError('Ошибка при запуске задачи');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Подключение к WebSocket для отслеживания статуса задачи
  useEffect(() => {
    console.log(taskId)
    if (!taskId) return;

    const socket = new WebSocket(`ws://localhost:8000/ws/task-status/${taskId}/`);

    socket.onopen = () => {
      console.log('WebSocket connected');
    };

    socket.onmessage = async (event) => {
      console.log('Message from server:', event.data);
      const data = JSON.parse(event.data);

      if (data.status === 'SUCCESS') {
        // Задача завершена, загружаем обновленные данные
        try {
          const response = await axios.get('/api/products/', {
            params: { load_products: true },
          });
          setProducts(response.data); // Обновляем список товаров
        } catch (err) {
          setError('Ошибка при загрузке товаров из базы данных');
          console.error(err);
        }
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    socket.onclose = () => {
      console.log('WebSocket closed');
    };

    return () => {
      socket.close();
    };
  }, [taskId]);



  return (
    <div className="container mt-5">
      <h1 className="text-center mb-4">Поиск товаров Ozon</h1>

      {/* Форма */}
      <form onSubmit={(e) => { e.preventDefault(); fetchProducts(); }} className="mb-4">
        <div className="row">
          <div className="col-md-3">
            <label className="form-label">Количество товаров</label>
            <input
              type="number"
              name="limit"
              className="form-control"
              value={filters.limit}
              onChange={handleInputChange}
              min="1"
            />
          </div>
          <div className="col-md-3 d-flex align-items-end">
            <div className="form-check">
              <input
                type="checkbox"
                name="update"
                className="form-check-input"
                checked={filters.update}
                onChange={handleInputChange}
              />
              <label className="form-check-label">Обновить товары</label>
            </div>
          </div>
          <div className="col-md-6 d-flex align-items-end">
            <button type="submit" className="btn btn-primary w-100">
              Найти товары
            </button>
          </div>
        </div>
      </form>

      {/* Список товаров */}
      {loading && <p>Загрузка...</p>}
      {error && <p className="text-danger">{error}</p>}
      <div className="row">
        {products.map((product) => (
          <div key={product.ozon_id} className="col-md-4 mb-4">
            <div className="card">
              <img
                src={product.image_url || 'https://via.placeholder.com/150'}
                alt={product.name}
                className="card-img-top"
              />
              <div className="card-body">
                <h5 className="card-title">{product.name}</h5>
                <p className="card-text">
                  Цена: {product.price} ₽<br />
                  Количество: {product.quantity}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;