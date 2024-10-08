// src/App.js
import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [formData, setFormData] = useState({ name: '', email: '', password: '', profilePicture: '' });
  const [token, setToken] = useState('');
  const [tipData, setTipData] = useState({ place: '', totalAmount: '', time: '' });
  const [tips, setTips] = useState([]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleTipChange = (e) => {
    setTipData({ ...tipData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:5000/register', formData);
      alert('User registered successfully');
    } catch (error) {
      alert(error.response.data.error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/login', { email: formData.email, password: formData.password });
      setToken(response.data.access_token);
      alert('Login successful');
    } catch (error) {
      alert(error.response.data.error);
    }
  };

  const handleAddTip = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:5000/tips', tipData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      alert('Tip added successfully');
      fetchTips(); // Refresh the tips list
    } catch (error) {
      alert(error.response.data.error);
    }
  };

  const fetchTips = async () => {
    try {
      const response = await axios.get('http://localhost:5000/tips', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setTips(response.data);
    } catch (error) {
      console.error('Error fetching tips:', error);
    }
  };

  return (
    <div>
      <h1>Tip Manager</h1>
      <form onSubmit={handleRegister}>
        <input type="text" name="name" placeholder="Name" onChange={handleChange} required />
        <input type="email" name="email" placeholder="Email" onChange={handleChange} required />
        <input type="password" name="password" placeholder="Password" onChange={handleChange} required />
        <input type="text" name="profilePicture" placeholder="Profile Picture URL" onChange={handleChange} />
        <button type="submit">Register</button>
      </form>
      <form onSubmit={handleLogin}>
        <input type="email" name="email" placeholder="Email" onChange={handleChange} required />
        <input type="password" name="password" placeholder="Password" onChange={handleChange} required />
        <button type="submit">Login</button>
      </form>
      <form onSubmit={handleAddTip}>
        <input type="text" name="place" placeholder="Place" onChange={handleTipChange} required />
        <input type="number" name="totalAmount" placeholder="Total Amount" onChange={handleTipChange} required />
        <input type="text" name="time" placeholder="Time" onChange={handleTipChange} required />
        <button type="submit">Add Tip</button>
      </form>
      <button onClick={fetchTips}>Fetch Tips</button>
      <ul>
        {tips.map((tip, index) => (
          <li key={index}>
            {tip.place}: ${tip.total_amount} at {tip.time}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
