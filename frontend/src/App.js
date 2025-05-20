import { ChakraProvider } from '@chakra-ui/react';
import LoginPage from './auth/LoginPage';

function App() {
  return (
    <ChakraProvider>
      <LoginPage />
    </ChakraProvider>
  );
}

export default App;
