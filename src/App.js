import {
  Center,
  Text,
  Heading,
  VStack,
  Button,
  useDisclosure,
} from "@chakra-ui/react";

import { useState, useEffect } from "react";
import TransactionsTable from "./components/TransactionsTable";
import { ChakraProvider } from "@chakra-ui/react";
import AddModal from "./components/AddModal";

function App() {
  const [transactions, setTransactions] = useState([]);
  /*const [rollups, setRollups] = useState([]);*/
  const { isOpen, onOpen, onClose } = useDisclosure();

  useEffect(() => {
    /*fetch("http://127.0.0.1:5000/transactions")
      .then((response) => response.json())
      .then((data) => {
        setRollups(data);
        let costAccumulator = 0;
        let valueAccumulator = 0;
        data.forEach((item) => {
          costAccumulator += item["purchased_price"];
          valueAccumulator += item["value_usd"];
        });
        let absoluteGain = valueAccumulator - costAccumulator;

        setPortfolioCost(costAccumulator);
        setPortfolioValue(valueAccumulator);
        setAbsoluteGain(absoluteGain);
        setTotalGainPercent((absoluteGain / costAccumulator) * 100);
      });*/
    fetch("http://127.0.0.1:5000/transactions")
      .then((response) => response.json())
      .then((data) => {
        console.log("neeha",data);
        var newdata = data["bitcoin"].concat(data["solana"]);
        setTransactions(newdata);
      });
  });
  /*}, [isOpen]);*/
  return (
    <ChakraProvider>
      <AddModal isOpen={isOpen} onOpen={onOpen} onClose={onClose}></AddModal>
      <Center bg="black" color="white" padding={8}>
        <VStack spacing={7}>
          <Heading>Crypto Portfolio</Heading>
          <Text>This is the current state of your portfolio</Text>
          <Button size="lg" colorScheme="teal" onClick={onOpen}>
            Add Transaction
          </Button>
          <TransactionsTable transactions={transactions}></TransactionsTable>
        </VStack>
      </Center>
    </ChakraProvider>
  );
}

export default App;
