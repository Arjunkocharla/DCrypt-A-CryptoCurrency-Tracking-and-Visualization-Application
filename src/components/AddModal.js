import React, { useState } from "react";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  VStack,
  Button,
  Input,
} from "@chakra-ui/react";

export default function AddModal({ isOpen, onClose }) {
  const [Type, setType] = useState("");
  const [Name, setName] = useState("");
  const [Symbol, setSymbol] = useState("");
  const [PurchasedPrice, setPurchasedPrice] = useState("");
  const [Date, setDate] = useState("");
  const [Coins, setCoins] = useState("");
  const [ValueUSD, setValueUSD] = useState("");

  const addTransaction = () => {
    const payload = JSON.stringify({
      name: Name,
      symbol: Symbol,
      type: Type,
      purchased_price: PurchasedPrice,
      date: Date,
      coins: Coins,
      value_usd : ValueUSD
    });
    console.log(payload);
    fetch("http://127.0.0.1:5000/transactions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload,
    })
      .then((response) => response.json())
      .then((data) => {
        onClose();
      });
  };

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add Transaction</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={8}>
              <Input
                value={Type}
                onChange={(e) => setType(e.target.value)}
                focusBorderColor="tomato"
                variant="flushed"
                placeholder="Type"
              />
              <Input
                value={Name}
                onChange={(e) => setName(e.target.value)}
                focusBorderColor="tomato"
                variant="flushed"
                placeholder="Name"
              />
              <Input
                value={Symbol}
                onChange={(e) => setSymbol(e.target.value)}
                focusBorderColor="tomato"
                variant="flushed"
                placeholder="Symbol"
              />
              <Input
                value={PurchasedPrice}
                onChange={(e) => setPurchasedPrice(e.target.value)}
                focusBorderColor="tomato"
                variant="flushed"
                placeholder="Price Purchased At"
              />
              <Input
                value={Date}
                onChange={(e) => setDate(e.target.value)}
                focusBorderColor="tomato"
                variant="flushed"
                placeholder="Transaction Date"
              />
              <Input
                value={Coins}
                onChange={(e) => setCoins(e.target.value)}
                focusBorderColor="tomato"
                variant="flushed"
                placeholder="Number of Coins"
              />
              <Input
                value={ValueUSD}
                onChange={(e) => setValueUSD(e.target.value)}
                focusBorderColor="tomato"
                variant="flushed"
                placeholder="Value USD"
              />
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button
              bg="tomato"
              color="white"
              mr={3}
              size="lg"
              onClick={addTransaction}
            >
              Add Transaction
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
}
