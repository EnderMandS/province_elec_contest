//
// Created by M on 2022/07/24.
//

#ifndef ELEC_CONTEST_USER_UART_H
#define ELEC_CONTEST_USER_UART_H

#include "main.h"
#include "FreeRTOS.h"
#include "cmsis_os2.h"
#include <string>
#include "queue.h"

namespace user_uart {
  class UartReceive {
  public:
    UartReceive(UART_HandleTypeDef *huart, uint32_t data_length, const std::string& queue_name);
    HAL_StatusTypeDef uartReceiveStart();
    HAL_StatusTypeDef uartReceiveStop();
    void uartCallback();

    xQueueHandle queue_handle;
    uint32_t length;

  private:
    uint8_t *buffer;
    UART_HandleTypeDef *huart;
  };
}

#endif //ELEC_CONTEST_USER_UART_H
