/*
 * J1939 Example Program
 *
 * author: Ethan Lew <elew@galois.com>
 *
 * Demonstrate the J1939 functionality implemented for the
 * cyberphys demonstrator.
 */

#include "can.h"
#include "j1939.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
  /* show example of pgn/id working */
  int32_t my_can_id;
  int32_t my_pgn = 60879;
  printf("My PGN: %d, My PGN from ID: %d\n", my_pgn,
         pgn_from_id(id_from_pgn(my_pgn)));

  /* show BAM packet creation and parameter extraction */
  uint32_t ret_pgn;
  uint16_t nbytes, npackets;
  can_frame my_packet[1];
  packet_bam(my_packet, 72, my_pgn);
  params_bam(my_packet, &ret_pgn, &nbytes, &npackets);
  printf("My BAM Attributes--PGN: %d, Bytes: %d, Packets: %d\n", ret_pgn,
         nbytes, npackets);

  /* show DT packet creation and parameter extraction */
  const char data[] = "test";
  char ret_data[10];
  uint8_t ret_size, ret_sidx;
  packet_dt(my_packet, 2, (void *)data, sizeof(data));
  params_dt(my_packet, &ret_sidx, (void *)ret_data, &ret_size);
  printf("My DT Attributes--Sequence Num: %d, Size: %d, Message: %s\n",
         ret_sidx, ret_size, ret_data);

  /* translate msg to packets, and then reconstruct the buffer */
  uint8_t np;
  const char msg[] = "This is a message for CAN BAM: Hello World\nThis is "
                     "another line\nAnd another one here\n";
  can_frame *packets = data_to_bam_can_frames(my_pgn, (void *)msg, sizeof(msg), &np);
  char *rmsg = (char *)bam_can_frames_to_data(packets);
  printf("Returned Message: %s\n", rmsg);

  /* free memory allocated by data_to_bam_can_frames and bam_can_frames_to_data */
  free(packets);
  free(rmsg);

  return 0;
}
