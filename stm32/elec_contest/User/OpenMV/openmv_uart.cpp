//
// Created by M on 2022/07/21.
//

#include "openmv_uart.h"
#include "FreeRTOS.h"
#include "usart.h"
#include "queue.h"

enum {
  NO_AVAILABLE_,
  RED_,
  GREEN,
  YELLOW_
};

auto openmv_uart = user_uart::UartReceive(&UART_HANDLE, DATA_LENGTH, "openmv uart queue");

extern "C" {
  /**
   * @brief
   * @param argument
   */
  _Noreturn void OpenMVUartTask(void *argument) {
    uint8_t data[DATA_LENGTH];
    openmv_uart.uartReceiveStart();
    for (;;) {
      xQueuePeek(openmv_uart.queue_handle, &data, portMAX_DELAY);
      if (data[0] > YELLOW_) {
        data[0] = NO_AVAILABLE_;
      }
    }
  }

  void uart5Callback() {
    openmv_uart.uartCallback();
  }
}


