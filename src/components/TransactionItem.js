import React from "react";

import { Tr, Td } from "@chakra-ui/react";

export default function TransactionItem({ transaction }) {
  return (
    <Tr>
      <Td>{transaction["name"]}</Td>
      <Td>{transaction["symbol"]}</Td>
      <Td>{transaction["type"]}</Td>
      <Td isNumeric>{transaction["coins"]}</Td>
      <Td isNumeric>$ {transaction["purchased_price"].toLocaleString()}</Td>
      <Td isNumeric>$ {transaction["value_usd"].toLocaleString()}</Td>
      <Td isNumeric>{transaction["date"]}</Td>
    </Tr>
  );
}
