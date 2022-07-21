//
// Created by M on 2022/07/21.
//

#ifndef ELEC_CONTEST_OPENMV_UART_H
#define ELEC_CONTEST_OPENMV_UART_H

#include "main.h"

#define UART5_DATA_LENGTH_ 1

typedef struct {
  uint8_t status[UART5_DATA_LENGTH_];
} Uart5Data;

enum {
  NO_AVAILABLE_,
  RED_,
  GREEN,
  YELLOW_
};

void uart5Callback(void);

extern Uart5Data uart5_data;

#endif //ELEC_CONTEST_OPENMV_UART_H
