//
// Created by M on 2022/07/21.
//

#include "openmv_uart.h"
#include "FreeRTOS.h"
#include "cmsis_os2.h"
#include "usart.h"
#include "queue.h"

Uart5Data uart5_buffer, uart5_data;
extern osMessageQueueId_t uart5_Data_QueueHandle;

/**
 * @brief 串口5接收数据处理任务，队列由串口DMA回调函数写入。
 * @param argument
 */
_Noreturn void OpenMVUartTask(void *argument) {
  __HAL_UART_ENABLE_IT(&huart5, UART_IT_IDLE);
  HAL_UART_Receive_DMA(&huart5, (uint8_t *) &uart5_buffer, UART5_DATA_LENGTH_);
  for (;;) {
    xQueuePeek(uart5_Data_QueueHandle, &uart5_data, portMAX_DELAY);
    if (uart5_data.status[0] > YELLOW_) {
      uart5_data.status[0] = NO_AVAILABLE_;
    }
  }
}

/**
 * @brief 串口5空闲中断接收回调函数，在usart.c中判断为DMA空闲中断后调用。将DMA中的数据存入队列，重新开始DMA接收。
 */
void uart5Callback(void) {
  BaseType_t xHigherPriorityTaskWoken = pdFALSE;
  xQueueOverwriteFromISR(uart5_Data_QueueHandle, &uart5_buffer, &xHigherPriorityTaskWoken);
  HAL_UART_Receive_DMA(&huart5, (uint8_t *) &uart5_buffer, UART5_DATA_LENGTH_);
}
