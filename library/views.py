from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Book, Author, Member, BorrowRecord
from .serializers import BookSerializer, AuthorSerializer, MemberSerializer, BorrowRecordSerializer

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

    @action(detail=True, methods=['get'])
    def records(self, request, pk=None):
        member = self.get_object()
        records = BorrowRecord.objects.filter(member=member)
        serializer = BorrowRecordSerializer(records, many=True)
        return Response(serializer.data)

class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer

    @action(detail=False, methods=['post'])
    def borrow(self, request):
        data = request.data
        book = Book.objects.get(id=data['book_id'])
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
        return Response(BorrowRecordSerializer(record).data)

    @action(detail=False, methods=['post'])
    def return_book(self, request):
        data = request.data
        record = BorrowRecord.objects.filter(book_id=data['book_id'], member_id=data['member_id'], is_returned=False).first()
        if not record:
            return Response({'error': 'No active borrow record found'}, status=404)
        record.return_date = data['return_date']
        record.is_returned = True
        record.save()
        record.book.availability_status = True
        record.book.save()
        return Response({'message': 'Book returned successfully'})
