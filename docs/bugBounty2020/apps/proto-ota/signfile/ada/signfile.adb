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

with GNAT.SHA256;     use GNAT.SHA256;
with GNAT.IO_Aux;

procedure SignFile
is
   PK : Signing_PK;
   SK : Signing_SK;
   SK_Raw : Bytes_32;

   function C is new
     Ada.Unchecked_Conversion (Binary_Message_Digest, Bytes_32);

begin
   if Argument_Count = 1 then
      declare
         FN : constant String := Argument (1);
         FH : Ada.Streams.Stream_IO.File_Type;
         FC : Ada.Streams.Stream_IO.Count;
         FL : Stream_Element_Offset;
      begin
         if GNAT.IO_Aux.File_Exists (FN) then
            Open (FH, In_File, FN);
            Put_Line ("Opened file OK");
            FC := Size (FH);
            Put_Line ("File size is" & FC'Img & " bytes");

            if FC < 1 then
               Put_Line ("File must be at least 1 byte long.");
               Close (FH);
               return;
            end if;

            if FC > Ada.Streams.Stream_IO.Count (SPARKNaCl.N32'Last) -
              SPARKNaCl.Sign.Sign_Bytes
            then
               Put_Line ("File too large.");
               Close (FH);
               return;
            end if;

            declare
               subtype M_Index is Stream_Element_Offset
                 range 1 .. Stream_Element_Offset (FC);
               subtype M_Buffer is Stream_Element_Array (M_Index);
               M  : M_Buffer;

               subtype SMB_Index is SPARKNaCl.N32
                 range 0 .. SPARKNaCl.N32 (FC) + SPARKNaCl.Sign.Sign_Bytes - 1;
               subtype SMB_Buffer is SPARKNaCl.Byte_Seq (SMB_Index);
               SM, M2 : SMB_Buffer;

               subtype MB_Index is N32 range 0 .. N32 (FC) - 1;
               subtype MB_Buffer is Byte_Seq (MB_Index);
               function MC is new Ada.Unchecked_Conversion
                 (M_Buffer, MB_Buffer);

               subtype SM_Index is Stream_Element_Offset
                 range 1 .. Stream_Element_Offset (FC) +
                            SPARKNaCl.Sign.Sign_Bytes;
               subtype SM_Buffer is Stream_Element_Array (SM_Index);
               function SMC is new Ada.Unchecked_Conversion
                 (SMB_Buffer, SM_Buffer);

               OK    : Boolean;
               M2Len : I32;
            begin
               M  := (others => 0);
               SM := (others => 0);
               Read (FH, M, FL);
               Put_Line ("Read" & FL'Img & " bytes OK");
               Close (FH);

               Put ("What's the password: ");

               declare
                  S : constant String := GNAT.IO_Aux.Get_Line;
               begin
                  if S'Length in 1 .. 64 then
                     SK_Raw := C (GNAT.SHA256.Digest (S));
                  else
                     Put_Line
                       ("Password must be between 1 and 64 characters long.");
                     return;
                  end if;
               end;

               Keypair_From_Bytes (SK_Raw, PK, SK);

               SPARKNaCl.Sign.Sign (SM, MC (M), SK);

               --  Sanitize SK and SK_Raw
               SK_Raw := (others => 0);
               pragma Inspection_Point (SK_Raw);
               SPARKNaCl.Sign.Sanitize (SK);

               DH ("PK ", Serialize (PK));

               DH ("Signed message is ", SM);

               --  Verify the signature using PK
               SPARKNaCl.Sign.Open (M2, OK, M2Len, SM, PK);

               if OK then
                  Put_Line ("Signature OK");
                  Put_Line ("M2Len is " & M2Len'Img);
                  DH ("M2 is ", M2 (0 .. (M2Len - 1)));
               else
                  Put_Line ("Signature does not verify.");
                  return;
               end if;

               Create (FH, Out_File, FN & ".sig");
               Write (FH, SMC (SM));
               Close (FH);

            end;
         else
            Put_Line ("File does not exist or not readable.");
         end if;
      end;
   else
      Put_Line ("Usage: signfile filename");
      Put_Line ("--  Signs filename and puts result in filename.sig");
   end if;

exception
   when E : others =>
      Put_Line (Exception_Information (E));
      Put_Line (GNAT.Traceback.Symbolic.Symbolic_Traceback (E));
end SignFile;
