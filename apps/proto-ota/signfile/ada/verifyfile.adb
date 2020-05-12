with SPARKNaCl;       use SPARKNaCl;
with SPARKNaCl.Sign;  use SPARKNaCl.Sign;
with SPARKNaCl.Debug; use SPARKNaCl.Debug;

with Ada.Command_Line;      use Ada.Command_Line;
with Ada.Exceptions;        use Ada.Exceptions;
with Ada.Streams;           use Ada.Streams;
with Ada.Streams.Stream_IO; use Ada.Streams.Stream_IO;
with Ada.Text_IO;           use Ada.Text_IO;
with Ada.Unchecked_Conversion;

with GNAT.Traceback;
with GNAT.Traceback.Symbolic;


with Interfaces;      use Interfaces;

with GNAT.IO_Aux;

procedure VerifyFile
is
   --  Generated from the secret pass-phrase
   Raw_PK : constant Bytes_32 :=
     (16#BA#, 16#FB#, 16#D4#, 16#BB#, 16#9F#, 16#8E#, 16#CE#, 16#C1#,
      16#EC#, 16#E7#, 16#42#, 16#D7#, 16#EA#, 16#3B#, 16#2E#, 16#E2#,
      16#E0#, 16#16#, 16#E3#, 16#0F#, 16#27#, 16#0B#, 16#AE#, 16#74#,
      16#B3#, 16#0B#, 16#ED#, 16#AC#, 16#33#, 16#47#, 16#01#, 16#FA#);

   PK : Signing_PK;
begin
   PK_From_Bytes (Raw_PK, PK);

   if Argument_Count = 1 then
      declare
         FN : constant String := Argument (1);
         FH : Ada.Streams.Stream_IO.File_Type;
         FC : Ada.Streams.Stream_IO.Count;
      begin
         if GNAT.IO_Aux.File_Exists (FN) then
            Open (FH, In_File, FN);
            Put_Line ("Opened file OK");
            FC := Size (FH);
            Put_Line ("File size is" & FC'Img & " bytes");

            if FC < 65 then
               Put_Line ("File must be at least 65 bytes long.");
               Close (FH);
               return;
            end if;

            declare
               subtype SM_Index is Stream_Element_Offset
                 range 1 .. Stream_Element_Offset (FC);
               subtype SM_Buffer is Stream_Element_Array (SM_Index);
               SM : SM_Buffer;

               subtype SMB_Index is N32 range 0 .. N32 (FC) - 1;
               subtype SMB_Buffer is SPARKNaCl.Byte_Seq (SMB_Index);
               function SMC is new Ada.Unchecked_Conversion
                 (SM_Buffer, SMB_Buffer);


--               subtype MB_Index is N32
--                 range 0 .. N32 (FC) - 1;
--               subtype MB_Buffer is Byte_Seq (MB_Index);
               M  : SMB_Buffer;

               FL   : Stream_Element_Offset;
               OK   : Boolean;
               MLen : I32;
            begin
               M  := (others => 0);
               SM := (others => 0);
               Read (FH, SM, FL);

               Put_Line ("Read" & FL'Img & " bytes OK");
               Close (FH);

               --  Verify the signature using PK
               SPARKNaCl.Sign.Open (M, OK, MLen, SMC (SM), PK);

               if OK then
                  Put_Line ("Signature OK");
                  Put_Line ("MLen is " & MLen'Img);
                  DH ("M is ", M (0 .. (MLen - 1)));
               else
                  Put_Line ("Signature does not verify.");
                  return;
               end if;

            end;
         else
            Put_Line ("File doesn not exist or not readable.");
         end if;
      end;

   else
      Put_Line ("Usage: verifyfile signed_filename");
   end if;

exception
   when E : others =>
      Put_Line (Exception_Information (E));
      Put_Line (GNAT.Traceback.Symbolic.Symbolic_Traceback (E));
end VerifyFile;
