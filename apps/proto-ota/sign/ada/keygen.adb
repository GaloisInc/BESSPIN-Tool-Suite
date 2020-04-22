with SPARKNaCl;       use SPARKNaCl;
with SPARKNaCl.Sign;  use SPARKNaCl.Sign;
with SPARKNaCl.Debug; use SPARKNaCl.Debug;

with Ada.Text_IO;     use Ada.Text_IO;
with Ada.Unchecked_Conversion;

with Interfaces;      use Interfaces;

with GNAT.SHA256;     use GNAT.SHA256;
with GNAT.IO_Aux;

procedure KeyGen
is
   PK1 : Signing_PK;
   SK1 : Signing_SK;
   PK2 : Signing_PK;
   SK2 : Signing_SK;
   SK_Raw : Bytes_32;

   function C is new
     Ada.Unchecked_Conversion (Binary_Message_Digest, Bytes_32);

   M      : constant Bytes_64 := (16#55#, others => 16#aa#);
   SM, M2 : Byte_Seq (0 .. 127);

   OK : Boolean;
   M2Len : I32;
begin

   Put ("What's the password: ");

   declare
      S : constant String := GNAT.IO_Aux.Get_Line;
   begin
      SK_Raw := C (GNAT.SHA256.Digest (S));

      DH ("SK_Raw is ", SK_Raw);

      Keypair_From_Bytes (SK_Raw, PK1, SK1);

      --  Modify SK_Raw and genereate SK2 and PK2 from it to get
      --  a different key pair
      SK_Raw (1) := SK_Raw (1) + 1;
      Keypair_From_Bytes (SK_Raw, PK2, SK2);

      DH ("PK1 is", Serialize (PK1));
      DH ("SK1 is", Serialize (SK1));

      Put_Line ("Case 1 - correct keys and message");
      SPARKNaCl.Sign.Sign (SM, M, SK1);
      DH ("SM is ", SM);
      SPARKNaCl.Sign.Open (M2, OK, M2Len, SM, PK1);

      if OK then
         Put_Line ("Signature OK");
         Put_Line ("M2Len is " & M2Len'Img);
         DH ("M2 is ", M2 (0 .. (M2Len - 1)));
      else
         Put_Line ("Signature NOT OK");
      end if;

      Put_Line ("Case 2 - same message, but wrong public key");
      SPARKNaCl.Sign.Open (M2, OK, M2Len, SM, PK2);
      if OK then
         Put_Line ("Signature OK");
         Put_Line ("M2Len is " & M2Len'Img);
         DH ("M2 is ", M2);
      else
         Put_Line ("Signature NOT OK");
      end if;

      Put_Line
        ("Case 3 - same message, correct public key, but wrong private key");
      SPARKNaCl.Sign.Sign (SM, M, SK2);
      SPARKNaCl.Sign.Open (M2, OK, M2Len, SM, PK1);

      if OK then
         Put_Line ("Signature OK");
         Put_Line ("M2Len is " & M2Len'Img);
         DH ("M2 is ", M2);
      else
         Put_Line ("Signature NOT OK");
      end if;

      Put_Line
        ("Case 4 - correct keys, but message corrupted");
      SPARKNaCl.Sign.Sign (SM, M, SK1);
      --  Corrupt SM data in some way
      SM (SM'Last) := SM (SM'Last) - 1;
      SPARKNaCl.Sign.Open (M2, OK, M2Len, SM, PK1);

      if OK then
         Put_Line ("Signature OK");
         Put_Line ("M2Len is " & M2Len'Img);
         DH ("M2 is ", M2);
      else
         Put_Line ("Signature NOT OK");
      end if;

      Put_Line
        ("Case 5 - correct keys, but signature corrupted");
      SPARKNaCl.Sign.Sign (SM, M, SK1);
      --  Corrupt SM sig in some way
      SM (SM'First) := SM (SM'First) - 1;
      SPARKNaCl.Sign.Open (M2, OK, M2Len, SM, PK1);

      if OK then
         Put_Line ("Signature OK");
         Put_Line ("M2Len is " & M2Len'Img);
         DH ("M2 is ", M2);
      else
         Put_Line ("Signature NOT OK");
      end if;
   end;
end KeyGen;
