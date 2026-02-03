CREATE TABLE books (
  index_no INT PRIMARY KEY,
  book_name VARCHAR(150),
  book_author VARCHAR(100),
  image_of_front_page VARCHAR(255),
  no_of_copies INT,
  year_published INT
);

INSERT INTO books VALUES
(1,'Clean Code','Robert Martin','clean_code.jpg',12,2008),
(2,'The Pragmatic Programmer','Andrew Hunt','pragmatic.jpg',8,1999),
(3,'Kubernetes in Action','Marko Luksa','k8s_action.jpg',10,2018),
(4,'Design Patterns','Erich Gamma','design_patterns.jpg',6,1994),
(5,'Refactoring','Martin Fowler','refactoring.jpg',9,1999),
(6,'Effective Java','Joshua Bloch','effective_java.jpg',11,2017),
(7,'Python Crash Course','Eric Matthes','python_crash.jpg',14,2016),
(8,'Fluent Python','Luciano Ramalho','fluent_python.jpg',7,2015),
(9,'You Don’t Know JS','Kyle Simpson','ydkjs.jpg',13,2014),
(10,'Introduction to Algorithms','CLRS','clrs.jpg',5,2009);
