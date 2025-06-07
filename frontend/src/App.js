import { ChakraProvider } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './auth/LoginPage';
import EntityList from './entities/EntityList';
import EntityForm from './entities/EntityForm';

function App() {
  const isAuthenticated = true; // Sostituisci con la tua logica di autenticazione

  return (
    <ChakraProvider>
      <Router>
        <Routes>
          <Route path="/login" element={!isAuthenticated ? <LoginPage /> : <Navigate to="/entities" />} />
          
          {/* Rotte protette */}
          <Route path="/entities" element={isAuthenticated ? <EntityList /> : <Navigate to="/login" />} />
          <Route path="/entities/new" element={isAuthenticated ? <EntityForm /> : <Navigate to="/login" />} />
          <Route path="/entities/edit/:id" element={isAuthenticated ? <EntityForm /> : <Navigate to="/login" />} />
          
          {/* Redirect alla pagina delle entità come home */}
          <Route path="/" element={<Navigate to="/entities" />} />
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

export default App;
