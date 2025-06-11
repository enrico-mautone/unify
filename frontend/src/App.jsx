import { Box, VStack, Heading } from '@chakra-ui/react';
import { renderComponent } from './utils/componentMapper';
import { loginLayout } from './data/loginLayout';

function App() {
  return (
    <Box 
      width="100%"
      minHeight="100%"
      display="flex" 
      flexDirection="column"
      alignItems="center" 
      justifyContent="flex-start"
      textAlign="center"
      bg="gray.50"
      p={4}
    >
      <VStack spacing={8} width="100%" maxW="container.md" mt={8} mb={8}>
        <Heading as="h1" size="2xl">
          Benvenuto in Unify
        </Heading>
        
        {/* Render the login layout */}
        <Box width="100%">
          {renderComponent(loginLayout.layout, 'login-layout')}
        </Box>
      </VStack>
    </Box>
  )
}

export default App
