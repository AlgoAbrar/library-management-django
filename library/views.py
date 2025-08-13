from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Book, Author, Member, BorrowRecord
from .serializers import BookSerializer, AuthorSerializer, MemberSerializer, BorrowRecordSerializer
from .permissions import IsLibrarianOrReadOnly


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly] 


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly] 


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated, IsAdminUser] 

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def records(self, request, pk=None):
        """Retrieve borrowing history for a specific member."""
        member = self.get_object()
        records = BorrowRecord.objects.filter(member=member)
        serializer = BorrowRecordSerializer(records, many=True)
        return Response(serializer.data)


class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAuthenticated] 

    @action(detail=False, methods=['post'])
    def borrow(self, request):
        """Borrow a book (must be available)."""
        data = request.data
        try:
            book = Book.objects.get(id=data['book_id'])
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)

        if not book.availability_status:
            return Response({'error': 'Book not available'}, status=400)

        book.availability_status = False
        book.save()

        record = BorrowRecord.objects.create(
            book=book,
            member=Member.objects.get(id=data['member_id']),
            borrow_date=data['borrow_date'],
            is_returned=False
        )
        return Response(BorrowRecordSerializer(record).data, status=201)

    @action(detail=False, methods=['post'])
    def return_book(self, request):
        """Return a borrowed book."""
        data = request.data
        record = BorrowRecord.objects.filter(
            book_id=data['book_id'],
            member_id=data['member_id'],
            is_returned=False
        ).first()

        if not record:
            return Response({'error': 'No active borrow record found'}, status=404)

        record.return_date = data['return_date']
        record.is_returned = True
        record.save()

        record.book.availability_status = True
        record.book.save()

        return Response({'message': 'Book returned successfully'}, status=200)
