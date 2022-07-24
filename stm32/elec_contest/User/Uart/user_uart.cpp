//
// Created by M on 2022/07/24.
//

#include "user_uart.h"
#include "usart.h"
#include "queue.h"


namespace user_uart {
  UartReceive::UartReceive(UART_HandleTypeDef *huart, uint32_t data_length, const std::string &queue_name) {
    this->huart = huart;
    length = data_length;
    buffer = new uint8_t[data_length];

    const osMessageQueueAttr_t queue_attributes = {
        .name = queue_name.c_str()
    };
    queue_handle = osMessageQueueNew(1, length, &queue_attributes);
  }

  void UartReceive::uartCallback() {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xQueueOverwriteFromISR((QueueHandle_t) queue_handle, buffer, &xHigherPriorityTaskWoken);
    HAL_UART_Receive_DMA(huart, (uint8_t *) buffer, length);
  }

  HAL_StatusTypeDef UartReceive::uartReceiveStart() {
    __HAL_UART_ENABLE_IT(huart, UART_IT_IDLE);
    return HAL_UART_Receive_DMA(huart, (uint8_t *) buffer, length);
  }

  HAL_StatusTypeDef UartReceive::uartReceiveStop() {
    __HAL_UART_DISABLE_IT(huart, UART_IT_IDLE);
    return HAL_UART_DMAStop(huart);
  }

}

