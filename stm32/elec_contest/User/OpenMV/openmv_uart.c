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
 * @brief ����5�������ݴ������񣬶����ɴ���DMA�ص�����д�롣
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
 * @brief ����5�����жϽ��ջص���������usart.c���ж�ΪDMA�����жϺ���á���DMA�е����ݴ�����У����¿�ʼDMA���ա�
 */
void uart5Callback(void) {
  BaseType_t xHigherPriorityTaskWoken = pdFALSE;
  xQueueOverwriteFromISR(uart5_Data_QueueHandle, &uart5_buffer, &xHigherPriorityTaskWoken);
  HAL_UART_Receive_DMA(&huart5, (uint8_t *) &uart5_buffer, UART5_DATA_LENGTH_);
}
