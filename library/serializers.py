from rest_framework import serializers
from .models import Book, Author, Member, BorrowRecord

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), source='author', write_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'author_id', 'ISBN', 'category', 'availability_status']

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'

class BorrowRecordSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True)
    member = MemberSerializer(read_only=True)
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(), source='member', write_only=True)

    class Meta:
        model = BorrowRecord
        fields = ['id', 'book', 'book_id', 'member', 'member_id', 'borrow_date', 'return_date', 'is_returned']
