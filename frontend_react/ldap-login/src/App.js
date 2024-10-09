import React, { useState } from 'react';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [userDetails, setUserDetails] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setUserDetails(null);

    const credentials = {
      username: username,
      password: password
    };

    try {
      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      });

      if (response.ok) {
        const data = await response.json();
        setUserDetails(data.user_details);
        setErrorMessage('');
      } else {
        const errorData = await response.json();
        setErrorMessage(errorData.detail);
        setUserDetails(null);
      }
    } catch (error) {
      setErrorMessage('An error occurred while logging in.');
      setUserDetails(null);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-sm">
        <h2 className="text-2xl font-bold text-center mb-6">Login</h2>

        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Username:</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              required
            />
          </div>
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2">Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
              required
            />
          </div>
          <div className="flex items-center justify-center">
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              Login
            </button>
          </div>
        </form>

        {/* Display error message */}
        {errorMessage && <p className="text-red-500 text-center mt-4">{errorMessage}</p>}

        {/* Display user details only if login is successful and no error */}
        {userDetails && (
          <div className="mt-6">
            <h3 className="text-lg font-bold">User Details:</h3>
            <p><strong>Common Name:</strong> {userDetails.commonName}</p>
            <p><strong>Surname:</strong> {userDetails.surName}</p>
            <p><strong>Email:</strong> {userDetails.mail ? userDetails.mail : "N/A"} </p>
            <p><strong>Mobile Number:</strong> {userDetails.mobileNumber ? userDetails.mobileNumber : "N/A"} </p>
            <p><strong>Title:</strong> {userDetails.title ? userDetails.title : "N/A"} </p>
            <p><strong>UID:</strong> {userDetails.uid}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default LoginPage;
