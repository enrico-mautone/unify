import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  Container,
  InputGroup,
  InputRightElement,
  IconButton,
  useToast
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import axios from 'axios';

// L'URL dell'API viene letto dalle variabili d'ambiente di Create React App
// Le variabili d'ambiente devono iniziare con REACT_APP_
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Debug
console.log('Using API URL:', API_URL);

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      console.log('Invio richiesta di login...');
      const response = await axios.post(
        `${API_URL}/login`,
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
          },
          withCredentials: true
        }
      );
      
      console.log('Risposta ricevuta:', response);
      
      if (response.data && response.data.access_token) {
        // Salva il token nel localStorage
        localStorage.setItem('token', response.data.access_token);
        
        toast({
          title: 'Accesso effettuato con successo!',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        
        // Reindirizza alla dashboard dopo il login
        // window.location.href = '/dashboard';
      } else {
        throw new Error('Token non ricevuto nella risposta');
      }
    } catch (error) {
      console.error('Errore durante il login:', error);
      const errorMessage = error.response?.data?.detail || 
                         error.message || 
                         'Errore durante il login. Riprova più tardi.';
      
      toast({
        title: 'Errore',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="container.sm" py={10}>
      <Box p={8} borderWidth={1} borderRadius="lg" boxShadow="lg">
        <VStack as="form" onSubmit={handleSubmit} spacing={6}>
          <Heading as="h1" size="xl" textAlign="center">
            Accedi al tuo account
          </Heading>
          
          <FormControl id="email" isRequired>
            <FormLabel>Indirizzo Email</FormLabel>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="esempio@email.com"
            />
          </FormControl>
          
          <FormControl id="password" isRequired>
            <FormLabel>Password</FormLabel>
            <InputGroup>
              <Input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="La tua password"
              />
              <InputRightElement>
                <IconButton
                  icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                  onClick={() => setShowPassword(!showPassword)}
                  variant="ghost"
                  aria-label={showPassword ? 'Nascondi password' : 'Mostra password'}
                />
              </InputRightElement>
            </InputGroup>
          </FormControl>
          
          <Button
            type="submit"
            colorScheme="blue"
            width="100%"
            isLoading={isLoading}
            loadingText="Accesso in corso..."
          >
            Accedi
          </Button>
        </VStack>
      </Box>
    </Container>
  );
};

export default LoginPage;
