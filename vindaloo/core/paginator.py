from math import ceil

from sqlalchemy.orm import Query

from .exceptions import InvalidPage, PageNotAnInteger


class Paginator:
    """
    The Paginator class is modelled after the Django Paginator class.

    Check out the docs on the Django Paginator for more information.
    """

    def __init__(self, items, per_page, max_per_page=0):
        """
        Creates a new Paginator instance.

        If per_page is 0 we return all items in one page. This is only
        the case if max_per_page is 0, otherwise we still paginate
        but using max_per_page as the page size.

        :param items: List of items to paginate or SQLAlchemy Query.
        :param per_page: Number of items per page, or 0 for no pagination.
        :param max_per_page: Max number of items per page (used by max_limit).
        """
        self.items = items
        self.per_page = int(per_page)
        self.max_per_page = int(max_per_page)

        # if items is an SQLAlchemy Query then call .count() instead of len().
        if isinstance(items, Query):
            self.count = items.count()
        else:
            self.count = len(items)

        # if per_page is 0, create one large page over the entire set.
        if self.per_page == 0:
            if self.max_per_page == 0:
                self.num_pages = 1
            else:
                self.num_pages = int(ceil(self.count / self.max_per_page))
        else:
            # per_page should never be higher than max_per_page, unless
            # per_page or max_per_page is 0, which means pagination is off.
            if self.per_page > self.max_per_page > 0:
                raise ValueError('per_page should not be higher than max_per_page')

            self.num_pages = int(ceil(self.count / self.per_page))

        # num_pages should never be 0, even when paginating an empty
        # list, num_pages will be set to 1 rather than 0.
        if self.num_pages == 0:
            self.num_pages = 1

        self.page_range = range(1, self.num_pages + 1)

    def page(self, page_number):
        return Page(self, page_number)


class Page:
    """
    The Page class is modelled after the Django Page class.

    Check out the docs on the Django Page for more information.
    """

    def __init__(self, paginator, number):
        # we only accept integer page numbers
        if type(number) is not int:
            raise PageNotAnInteger('{} is not an integer'.format(number))

        # make sure we get a page in range
        if number < 1 or number > paginator.num_pages or number == 0:
            raise InvalidPage('{} is not a valid page number'.format(number))

        self.paginator = paginator
        self.number = number
        self.offset = (self.number - 1) * self.paginator.per_page
        self.object_list = self.paginator.items[self.offset:self.end_index()]

    def has_next(self):
        return self.number < self.paginator.num_pages

    def has_previous(self):
        return self.number > 1

    def has_other_pages(self):
        return self.paginator.num_pages > 1

    def next_page_offset(self):
        if self.has_next():
            return self.offset + self.paginator.per_page
        else:
            raise InvalidPage('Next page does not exist')

    def previous_page_offset(self):
        if self.has_previous():
            return self.offset - self.paginator.per_page
        else:
            raise InvalidPage('Previous page does not exist')

    def next_page_number(self):
        if self.has_next():
            return self.number + 1
        else:
            raise InvalidPage('Next page does not exist')

    def previous_page_number(self):
        if self.has_previous():
            return self.number - 1
        else:
            raise InvalidPage('Previous page does not exist')

    def start_index(self):
        return self.offset + 1

    def end_index(self):
        if self.paginator.per_page == 0:
            if self.paginator.max_per_page == 0:
                return self.offset + self.paginator.count
            else:
                return self.offset + self.paginator.max_per_page
        else:
            return self.offset + self.paginator.per_page
